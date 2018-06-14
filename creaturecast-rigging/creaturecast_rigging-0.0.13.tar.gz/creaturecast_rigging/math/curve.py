import creaturecast_rigging.math.vector as vec
import creaturecast_rigging.math.matrix as mat


class Curve(object):
    def __init__(self, *args):
        super(Curve, self).__init__()
        self.points = list(args)

        for i, point in enumerate(self.points):
            if isinstance(point, mat.Matrix):
                self.points[i] = point.get_translate()


        #self.points.insert(-2, self.points[-2].average(self.points[-1]))
        #self.points.insert(1, self.points[0].average(self.points[1]))

        self.virtual_points = []

        for i in range(len(self.points)):
            self.virtual_points.append(self.points[i])
            if i not in [0, len(self.points)-1, len(self.points)-2]:
                self.virtual_points.append(self.points[i].average(self.points[i+1]))
                self.virtual_points.append(self.points[i].average(self.points[i+1]))

        degree = 2

        self.spans = [x for x in chunks(self.virtual_points, degree+1)]

    def get_point(self, parameter):
        length = 1.0 / (len(self.spans))
        for i in range(len(self.spans)):
            if parameter >= length*i and parameter <= length*(i+1):
                old_min = length*i
                old_max = length*(i+1)
                old_range = (old_max - old_min)
                new_range = (1.0 - 0.0)
                sub_parameter = (((parameter - old_min) * new_range) / old_range) + 0.0
                point_a = self.spans[i][0].average(self.spans[i][1], weight=sub_parameter)
                point_b = self.spans[i][1].average(self.spans[i][2], weight=sub_parameter)
                return point_a.average(point_b, weight=sub_parameter)
        raise Exception()


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def plot_points(control_points, count):
    vectors = [vec.Vector(*x) for x in control_points]
    curve = Curve(*vectors)
    for i in range(count):
        yield curve.get_point(1.0/count*i)
