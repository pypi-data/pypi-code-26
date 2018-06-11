import sys
from time import time
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from .utils import Filtration, Grid, PersistentHomology


class Cloud():
    def __init__(self, data=None, csv=None):
        if (data is not None and csv is not None) or (data is None and csv is None):
            raise ValueError("You should instanciate with either data or CSV file")
        if data is not None:
            self.data = data
            self.dimension, self.N = self.data.shape
            # self.kde = lambda x: self.new_kde(x, 0.3)
            self.kde = stats.gaussian_kde(self.data)
        if csv is not None:
            f = open(csv, 'r')
            rows = f.readlines()
            self.data = np.array([[float(x) for x in row.split(";")] for row in rows])
            self.dimension, self.N = self.data.shape
            self.kde = stats.gaussian_kde(self.data)

    def new_kde(self, data, epsilon):
        values = []
        dim, N = data.shape
        for j in range(N):
            x = data[:,j]
            value = 0
            for i in range(self.N):
                point = self.data[:,i]
                if np.linalg.norm(x-point) < epsilon:
                    value += 1
            values.append(float(value))
        return values

    def size(self):
        return [(row.min(), row.max()) for row in self.data]

    def grid(self, n, margin=0):
        return Grid(self, n, margin)

    def filtration(self, n):
        return Filtration(self, n)

    def persistent_homology(self, n=10, margin=0.1, verbose=False):
        if verbose:
            t0 = time()

        if verbose:
            t = time()
            sys.stderr.write("Building filtration... \n")
        filtration = Filtration(self, n, margin=margin, verbose=verbose)
        if verbose:
            sys.stderr.write("Done! (%f s)\n" % (time() - t))

        if verbose:
            t = time()
            sys.stderr.write("Calculating persistent homology...\n")
        persistent_homology = PersistentHomology(filtration, verbose=verbose)
        if verbose:
            sys.stderr.write("Done! (%f s)\n" % (time() - t))

        if verbose:
            sys.stderr.write("Total time: %f s\n" % (time() - t0))

        return persistent_homology

    def plot(self):
        if self.dimension == 1:
            data2D = np.vstack((self.data, np.zeros(self.N)))
            plt.scatter(*data2D)
            plt.show()
        elif self.dimension == 2:
            plt.scatter(*self.data)
            plt.axis('equal')
            plt.show()
        elif self.dimension == 3:
            data = self.data
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(*self.data)
            # Make equal axis with a fake bounding box
            max_range = max([M - m for m, M in self.size()])
            average= [0.5*(m+M) for m, M in self.size()]
            Xb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][0].flatten() + average[0]
            Yb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][1].flatten() + average[1]
            Zb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][2].flatten() + average[2]
            for xb, yb, zb in zip(Xb, Yb, Zb):
               ax.plot([xb], [yb], [zb], 'w')

            plt.show()
        else:
            print "You'll have to imagine it"

    def export_to_csv(self, file):
        try:
            f = open(file, 'r+')
        except IOError:
            f = open(file, 'w')
        for row in self.data:
            f.write(";".join(str(x) for x in row)+'\n')
        f.close()

    def __repr__(self):
        return "<Data cloud of R^%d with %d points>" % (self.dimension, self.N)


class S0(Cloud):
    def __init__(self, r=1, err=0, N=1000):
        self.radius = r
        self.error = err

        x = r*(2*np.random.randint(2, size=N)-1) + np.random.normal(0, err, N)
        data = np.array([x])
        Cloud.__init__(self, data=data)


class S1(Cloud):
    def __init__(self, center=(0, 0), r=1, err=0, N=1000):
        self.center = center
        self.radius = r
        self.error = err

        a, b = center
        t = np.random.uniform(0, 2 * np.pi, N)
        x = a + r * np.cos(t) + np.random.normal(0, err, N)
        y = b + r * np.sin(t) + np.random.normal(0, err, N)
        data = np.vstack((x, y))
        Cloud.__init__(self, data=data)


class S2(Cloud):
    def __init__(self, center=(0, 0, 0), r=1, err=0, N=1000):
        self.center = center
        self.radius = r
        self.error = err

        a, b, c = center
        u = np.random.random(N)
        v = np.random.random(N)
        theta = np.arccos(2*v-1)
        phi = 2*np.pi*u
        x = r * np.sin(theta) * np.cos(phi) + np.random.normal(0, err, N)
        y = r * np.sin(theta) * np.sin(phi) + np.random.normal(0, err, N)
        z = r * np.cos(theta) + np.random.normal(0, err, N)
        data = np.vstack((x, y, z))
        Cloud.__init__(self, data=data)


class T2(Cloud):
    def __init__(self, a=1, b=2, err=0, N=1000):
        self.radius_int = a
        self.radius_ext = b
        self.error = err

        x = []
        y = []
        z = []
        cont = 0
        while cont < N:
            u = np.random.uniform()
            v = np.random.uniform()
            w = np.random.uniform()
            
            theta = 2*np.pi*u
            phi = 2*np.pi*v
            if w > (b + a*np.cos(theta)) / (a + b):
                continue
            else:
                z.append(np.cos(phi)*(b + a*np.cos(theta)) + np.random.normal(0, err))
                x.append(np.sin(phi)*(b + a*np.cos(theta)) + np.random.normal(0, err))
                y.append(a*np.sin(theta) + np.random.normal(0, err))
                cont += 1
        data = np.array([x, y, z])
        Cloud.__init__(self, data=data)

class T2_old(Cloud):
    # **** NOT UNIFORMLY DISTRIBUTED ****
    def __init__(self, a=1, b=2, err=0, N=1000):
        self.radius_int = a
        self.radius_ext = b
        self.error = err

        theta = np.random.uniform(0, 2 * np.pi, N)
        phi = np.random.uniform(0, 2 * np.pi, N)
        x = np.cos(theta)*(b + a*np.cos(phi)) + np.random.normal(0, err, N)
        y = np.sin(theta)*(b + a*np.cos(phi)) + np.random.normal(0, err, N)
        z = a*np.sin(phi) + np.random.normal(0, err, N)
        data = np.vstack((x, y, z))
        Cloud.__init__(self, data=data)


class RP2(Cloud):
    # **** NOT UNIFORMLY DISTRIBUTED ****
    def __init__(self, err=0, N=1000):
        self.error = err

        # Using Hilbert and Cohn-Vossen map on S2
        u = np.random.random(N)
        v = np.random.random(N)
        theta = np.arccos(2*v-1)
        phi = 2*np.pi*u
        a = np.sin(theta) * np.cos(phi)
        b = np.sin(theta) * np.sin(phi)
        c = np.cos(theta)
        x = a*b + np.random.normal(0, err, N)
        y = b*c + np.random.normal(0, err, N)
        z = a*c + np.random.normal(0, err, N)
        t = a**2-b**2 + np.random.normal(0, err, N)
        data = np.vstack((x, y, z, t))
        Cloud.__init__(self, data=data)


class S1vS1(Cloud):
    def __init__(self, r=1, err=0, N=1000):
        self.radius = r
        self.error = err

        up = S1(center=(0, r), r=1, err=err, N=N/2)
        down = S1(center=(0, -r), r=1, err=err, N=N/2)
        data = np.hstack((up.data, down.data))
        Cloud.__init__(self, data=data)
