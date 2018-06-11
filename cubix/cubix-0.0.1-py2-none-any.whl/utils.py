import time
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from itertools import combinations, product
from sets import Set

from .debug import debugger


class CSimplex():
    def __init__(self, root, directions, value=0, filtration=None):
        self.root = root
        self.directions = directions
        self.value = value
        self.filtration = filtration
        self.homology_class = None

    @property
    def dimension(self):
        return len(self.directions)

    @property
    def space_dimension(self):
        return len(self.root)

    @property
    def points(self):
        simplex_points = [self.root]
        for direction in self.directions:
            new_points = []
            for point in simplex_points:
                new_point = CSimplex.point_expand(point, direction)
                new_points.append(new_point)
            simplex_points.extend(new_points)
        return simplex_points

    @staticmethod
    def point_expand(point, direction):
        new_point = list(point)
        new_point[direction] += 1
        return tuple(new_point)

    @staticmethod
    def directions_pop(directions, direction):
        new_directions = list(directions)
        new_directions.remove(direction)
        return tuple(new_directions)

    def border(self):
        border_list = []
        for direction in self.directions:
            new_directions = CSimplex.directions_pop(self.directions, direction)
            new_point = CSimplex.point_expand(self.root, direction)
            if self.filtration is not None:
                border_list.append(self.filtration.simplexes[(self.root, new_directions)])
                border_list.append(self.filtration.simplexes[(new_point, new_directions)])
            else:
                border_list.append(CSimplex(self.root, new_directions))
                border_list.append(CSimplex(new_point, new_directions))
        return border_list

    def diferencial(self):
        return sum(s.homology_class for s in self.border())

    def __hash__(self):
        return hash((self.root, self.directions))

    def __eq__(self, other):
        return self.root == other.root and self.directions == other.directions

    def __ne__(self, other):
        return self.root != other.root or self.directions != other.directions

    def __str__(self):
        return "S(%s,%s)" % (str(self.root), str(self.directions))

    def __repr__(self):
        return self.__str__()


class Filtration():
    def __init__(self, cloud, precission, margin=0, pruning=0, verbose=False):
        self.cloud = cloud
        self.dimension = cloud.dimension
        self.precission = precission

        if verbose:
            t0 = time.time()

        if verbose:
            sys.stderr.write("    Building grid...")
            t = time.time()
        self.grid = Grid(cloud, precission, margin)
        if verbose:
            sys.stderr.write("    Done! (%f s)\n" % (time.time()-t))

        if verbose:
            sys.stderr.write("    Giving value to points...")
            t = time.time()
        self.values = self.grid.evaluate(cloud.kde)
        if verbose:
            sys.stderr.write("    Done! (%f s)\n" % (time.time()-t))

        # if verbose:
        #     sys.stderr.write("    Check for repeated values...")
        #     t = time.time()
        # values = list(self.values.ravel())
        # for x in values:
        #     if values.count(x) > 1:
        #         sys.stderr.write("\n*** ALERTA *** Hay valores repetidos en la filtracion!!")
        # if verbose:
        #     sys.stderr.write("    -> Done! (%f s)" % (time.time()-t))

        if verbose:
            sys.stderr.write("    Building all simplexes...")
            t = time.time()
        self.build_simplexes()
        if verbose:
            sys.stderr.write("    Done! (%f s)\n" % (time.time()-t))

        if verbose:
            sys.stderr.write("    Sorting...")
            t = time.time()
        self.body = sorted(self.simplexes.values(),
                           key=lambda x: (x.value, x.dimension, x.root, x.directions))
        if verbose:
            sys.stderr.write("    Done! (%f s)\n" % (time.time()-t))

        if pruning:
            self.prune(pruning)

        if verbose:
            sys.stderr.write("  Total time: %f s\n" % (time.time()-t0))

    def build_simplexes(self):
        self.simplexes = {}
        maximum = max(self.values.ravel())
        for dim in range(self.dimension+1):
            for point in self.grid.positions:
                possible_directions = self.grid.possible_directions(point)
                for directions in combinations(possible_directions, dim):
                    dirs = tuple(directions)
                    simplex = CSimplex(point, dirs, filtration=self)
                    if dim == 0:
                        simplex.value = 1 - self.values[point]/maximum
                    else:
                        simplex.value = max(s.value for s in simplex.border())
                    self.simplexes[(point, dirs)] = simplex

    def prune(self, n):
        self.body = self[n]

    def sorted_points(self):
        return sorted(self.grid.positions, key=lambda x: self.values[x])

    def __getitem__(self, n):
        for s in self.body:
            if s.value < n:
                yield s
            else:
                break

    def __len__(self):
        return len(self.body)

    def __repr__(self):
        return "<Filtration of R^%d with %d cSimplexes>" \
                % (self.dimension, len(self))


class Grid():
    def __init__(self, cloud, precission, margin=0):
        self.dimension = cloud.dimension
        self.precission = precission
        self.size = []
        mounting = []
        for row in cloud.data:
            m = row.min()
            M = row.max()
            if margin:
                L = M-m
                m -= L*margin
                M += L*margin
            self.size.append((m, M))
            mounting.append(np.linspace(m, M, num=precission))
        self.mesh = np.meshgrid(*mounting)

    @property
    def epsilon(self):
        return [(M - m)/self.precission for m, M in self.size]

    @property
    def shape(self):
        return tuple(self.dimension * [self.precission])

    @property
    def positions(self):
        return [x for x in product(range(self.precission), repeat=self.dimension)]

    def possible_directions(self, point):
        directions = range(self.dimension)
        for i, coordinate in enumerate(point):
            if coordinate == self.precission-1:
                directions.remove(i)
        return directions

    def evaluate(self, function):
        data_ravel = np.vstack([line.ravel() for line in self.mesh])
        values = function(data_ravel)
        return np.reshape(values, self.shape)

    def __getitem__(self, position):
        point = [self.mesh[i][position] for i in range(self.dimension)]
        return tuple(point)

    def __repr__(self):
        return "<Grid of R^%d with shape %s>" % (self.dimension, str(self.shape()))


class HomologyClass():

    def __init__(self, homology, dimension, generators=[], representants=[]):
        self.homology = homology
        self.dimension = dimension
        self.generators = Set(generators)
        self.representants = Set(representants)

    def collapse(self, other):
        other.representants |= self.representants
        for rep in self.representants:
            rep.homology_class = other
        self.homology._classes[self.dimension].remove(self)

    def add(self, other):
        self.generators ^= other.generators
        for _class in self.homology._classes[self.dimension]:
            if self.generators == _class.generators and _class is not self:
                self.collapse(_class)

    def __nonzero__(self):
        if len(self.generators) == 0:
            return False
        else:
            return True

    def __add__(self, other):
        new_class = HomologyClass(self.homology, self.dimension)  # No representants in result
        new_class.generators = self.generators ^ other.generators
        return new_class

    # Not sure if I really need this
    def __radd__(self, other):
        if other:
            return other.__add__(self)
        else:
            return self

    def __str__(self):
        return "[ %s ]" % " + ".join(g.__str__() for g in self.generators)

    def __repr__(self):
        return self.__str__()


class HomologyGenerator():

    def __init__(self, homology, dimension, born_time):
        self.homology = homology
        self.dimension = dimension
        self.born = born_time
        self.death = 1
        self.id = self.homology.generator_index
        self.homology.generator_index += 1

    def die(self, death_time):
        self.death = death_time

    def life(self):
        return self.death - self.born

    def becomes(self, to_class):
        # print self, "->", to_class
        # print "Current list of classes dimension %d: " % self.dimension, self.homology._classes[self.dimension][:]
        for _class in self.homology._classes[self.dimension][:]:
            if self in _class.generators:
                # print self, " is in class ", _class
                _class.generators.remove(self)
                _class.add(to_class)

    def __str__(self):
        return "g%d" % self.id

    def __repr__(self):
        return self.__str__()


class PersistentHomology():
    def __init__(self, filtration, verbose=False):
        self.filtration = filtration
        self.dimension = filtration.dimension
        self.generator_index = 1
        self.holes = [[] for i in range(self.dimension+1)]

        self.calculate(verbose=verbose)

    def calculate(self, verbose=False):
        __NULLCLASS_ = [HomologyClass(self, i) for i in range(self.dimension+1)]
        self._classes = [[__NULLCLASS_[i]] for i in range(self.dimension+1)]
        if verbose:
            total = len(self.filtration.body)
            cont = 1
            sys.stderr.write("  Starting calculate..\n")
        for simplex in self.filtration.body:
            if simplex.value > 0.9:
                break
            if verbose:
                sys.stderr.write("\033[F")
                sys.stderr.write("  Processing simplex %d of %d\n" %(cont, total))
                cont += 1
            dim = simplex.dimension
            t = simplex.value
            d = simplex.diferencial()
            # print "Value: ", t
            # print "Simplex: %s (dim %d)" % (simplex, dim)
            # print "Diferencial: ", d
            # for i, s in enumerate(simplex.border()):
            #     print "--> Face %d: %s (class %s)" % (i+1, s, s.homology_class) 
            if d:
                # Kill generator
                younger = max(d.generators, key=lambda x: x.born)
                younger.becomes(d + HomologyClass(self, dim, generators=[younger]))
                younger.die(death_time=t)
                if younger.life() == 0:
                    self.holes[dim-1].remove(younger)
                simplex.homology_class = __NULLCLASS_[dim]
            else:
                # New generator
                new_generator = HomologyGenerator(self, dimension=dim, born_time=t)
                self.holes[dim].append(new_generator)
                new_class = HomologyClass(self, dim, generators=[new_generator], representants=[simplex])
                self._classes[dim].append(new_class)
                simplex.homology_class = new_class
            # print "Class: ", simplex.homology_class
            # print "--------"

    def detail(self):
        for dim in range(self.dimension):
            print "Dimension %d:" % dim
            if self.holes[dim]:
                for g in self.holes[dim]:
                    print "   %f -> %f  (%lf)" % (g.born, g.death, g.life())
            else:
                print "    No holes"

    def persistence_diagram(self, dimensions="all"):
        CLASSES_COLORS = {
            0: 'red',
            1: 'green',
            2: 'fuchsia',
            3: 'blue',
            4: 'turquoise',
            5: 'lime',
            6: 'purple',
            7: 'gold',
            8: 'brown',
            9: 'navy',
        }

        MAX_COLORS = len(CLASSES_COLORS)

        if dimensions == "all":
            dimensions = range(self.dimension+1)

        plt.title("Persistence diagram")
        plt.plot((0, 1), (0, 1), color='gray')
        plt.xlim([-0.05, 1.05])
        plt.ylim([-0.05, 1.05])
        handles = []
        for dim in dimensions:
            if not self.holes[dim]:
                continue
            for hclass in self.holes[dim]:
                x = [hclass.born, hclass.born]
                y = [hclass.born, hclass.death]
                plt.plot(x, y, linewidth=2.0, color=CLASSES_COLORS[dim % MAX_COLORS])
            handles.append(mpatches.Patch(color=CLASSES_COLORS[dim % MAX_COLORS], label='H%d' % dim))
        plt.legend(handles=handles, loc=4)
        plt.show()
