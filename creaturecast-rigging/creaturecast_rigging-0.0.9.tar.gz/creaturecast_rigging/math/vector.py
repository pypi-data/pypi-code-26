import math


class Vector(object):
    def __init__(self, *args):
        super(Vector, self).__init__()

        self.values = [0.0, 0.0, 0.0]
        if args:
            if not all(isinstance(x, float) for x in args):
                raise Exception('Vector values must be type: float, not : %s' % [type(x) for x in args])
            if isinstance(args[0], Vector):
                self.values = args[0].values
            else:
                self.values = args

    def __repr__(self):
        return '< %s %s >' % (self.__class__.__name__, self.values)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __add__(self, other):
        """
        Adds two vectors together.
        """
        return Vector(*[self[i] + other[i] for i in range(len(self))])

    def __sub__(self, other):
        """
        Subtracts two vectors.
        """
        return Vector(*[self[i] - other[i] for i in range(len(self))])

    def __iter__(self):
        for value in self.values:
            yield value

    def __div__(self, other):
        if isinstance(other, Vector):
            return Vector(*[self[i] / other[i] for i in range(len(self))])
        else:
            return Vector(*[self[i] / other for i in range(len(self))])

    def __mul__(self, other):
        if isinstance(other, Vector):
            return Vector(*[self[i] * other[i] for i in range(len(self))])
        else:
            return Vector(*[self[i] * other for i in range(len(self))])

    def length(self):
        return self.mag()

    def mag(self):
        """
        Returns magnitude (length) of a vector.
        """
        return math.sqrt(sum(self[i]**2 for i in range(len(self))))

    def normalize(self):
        vec_mag = self.mag()
        return Vector(*[self[i] / vec_mag for i in range(len(self))])

    def cross(self, other):
        """
        Returns cross product of two 3D vectors.
        Use for up vector
        """
        return Vector(*[
            self[1] * other[2] - self[2] * other[1],
            self[2] * other[0] - self[0] * other[2],
            self[0] * other[1] - self[1] * other[0]
        ])

    def dot(self, other):
        """
        Returns dot product of two 3D vectors.
        """
        return sum([p * q for p, q in zip(self, other)])

    def average(self, other, weight=0.5):
        return (other * (1.0-weight)) + (self * weight)


def add_vectors(vectors):
    vector = Vector()
    for i in range(len(vectors)):
        vector += vectors[i]
    return vector
