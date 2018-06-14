import math
import creaturecast_rigging.math.vector as vec


class Matrix(object):
    def __init__(self, *args):
        super(Matrix, self).__init__()
        self.values = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]

        if args:
            if isinstance(args[0], Matrix):
                self.values = args[0].values
            elif not all(isinstance(x, float) for x in args):
                raise Exception('Matrix values must be type: float, not : %s' % [type(x) for x in args])
            elif len(args) == 16:
                self.values = map(float, list(args))
            elif len(args) == 3:
                self.set_translate(args)
            else:
                raise Exception('Need to enter exactly 16 values to create a Matrix.')

    def __len__(self):
        return len(self.values)

    def __getitem__(self, i):
        return self.values[i]

    def __iter__(self):
        for i in range(len(self.values)):
            yield self.values[i]

    def __repr__(self):
        return '< %s %s >' % (self.__class__.__name__, self.values)

    def __mul__(self, other):

        m1_0,  m1_1,  m1_2,  m1_3, \
        m1_4,  m1_5,  m1_6,  m1_7, \
        m1_8,  m1_9,  m1_10, m1_11, \
        m1_12, m1_13, m1_14, m1_15 = self.values

        m2_0,  m2_1,  m2_2,  m2_3, \
        m2_4,  m2_5,  m2_6,  m2_7, \
        m2_8,  m2_9,  m2_10, m2_11, \
        m2_12, m2_13, m2_14, m2_15 = other.values

        new_values = [m2_0 * m1_0 + m2_1 * m1_4 + m2_2 * m1_8 + m2_3 * m1_12,
              m2_0 * m1_1 + m2_1 * m1_5 + m2_2 * m1_9 + m2_3 * m1_13,
              m2_0 * m1_2 + m2_1 * m1_6 + m2_2 * m1_10 + m2_3 * m1_14,
              m2_0 * m1_3 + m2_1 * m1_7 + m2_2 * m1_11 + m2_3 * m1_15,

              m2_4 * m1_0 + m2_5 * m1_4 + m2_6 * m1_8 + m2_7 * m1_12,
              m2_4 * m1_1 + m2_5 * m1_5 + m2_6 * m1_9 + m2_7 * m1_13,
              m2_4 * m1_2 + m2_5 * m1_6 + m2_6 * m1_10 + m2_7 * m1_14,
              m2_4 * m1_3 + m2_5 * m1_7 + m2_6 * m1_11 + m2_7 * m1_15,

              m2_8 * m1_0 + m2_9 * m1_4 + m2_10 * m1_8 + m2_11 * m1_12,
              m2_8 * m1_1 + m2_9 * m1_5 + m2_10 * m1_9 + m2_11 * m1_13,
              m2_8 * m1_2 + m2_9 * m1_6 + m2_10 * m1_10 + m2_11 * m1_14,
              m2_8 * m1_3 + m2_9 * m1_7 + m2_10 * m1_11 + m2_11 * m1_15,

              m2_12 * m1_0 + m2_13 * m1_4 + m2_14 * m1_8 + m2_15 * m1_12,
              m2_12 * m1_1 + m2_13 * m1_5 + m2_14 * m1_9 + m2_15 * m1_13,
              m2_12 * m1_2 + m2_13 * m1_6 + m2_14 * m1_10 + m2_15 * m1_14,
              m2_12 * m1_3 + m2_13 * m1_7 + m2_14 * m1_11 + m2_15 * m1_15]

        return Matrix(*new_values)

    def __imul__(self, other):

        """Multiplies this Matrix44 by another, called by the *= operator."""

        m1_0,  m1_1,  m1_2,  m1_3, \
        m1_4,  m1_5,  m1_6,  m1_7, \
        m1_8,  m1_9,  m1_10, m1_11, \
        m1_12, m1_13, m1_14, m1_15 = self.values

        m2_0,  m2_1,  m2_2,  m2_3, \
        m2_4,  m2_5,  m2_6,  m2_7, \
        m2_8,  m2_9,  m2_10, m2_11, \
        m2_12, m2_13, m2_14, m2_15 = other.values


        self.values = [ m2_0 * m1_0 + m2_1 * m1_4 + m2_2 * m1_8 + m2_3 * m1_12,
                    m2_0 * m1_1 + m2_1 * m1_5 + m2_2 * m1_9 + m2_3 * m1_13,
                    m2_0 * m1_2 + m2_1 * m1_6 + m2_2 * m1_10 + m2_3 * m1_14,
                    m2_0 * m1_3 + m2_1 * m1_7 + m2_2 * m1_11 + m2_3 * m1_15,

                    m2_4 * m1_0 + m2_5 * m1_4 + m2_6 * m1_8 + m2_7 * m1_12,
                    m2_4 * m1_1 + m2_5 * m1_5 + m2_6 * m1_9 + m2_7 * m1_13,
                    m2_4 * m1_2 + m2_5 * m1_6 + m2_6 * m1_10 + m2_7 * m1_14,
                    m2_4 * m1_3 + m2_5 * m1_7 + m2_6 * m1_11 + m2_7 * m1_15,

                    m2_8 * m1_0 + m2_9 * m1_4 + m2_10 * m1_8 + m2_11 * m1_12,
                    m2_8 * m1_1 + m2_9 * m1_5 + m2_10 * m1_9 + m2_11 * m1_13,
                    m2_8 * m1_2 + m2_9 * m1_6 + m2_10 * m1_10 + m2_11 * m1_14,
                    m2_8 * m1_3 + m2_9 * m1_7 + m2_10 * m1_11 + m2_11 * m1_15,

                    m2_12 * m1_0 + m2_13 * m1_4 + m2_14 * m1_8 + m2_15 * m1_12,
                    m2_12 * m1_1 + m2_13 * m1_5 + m2_14 * m1_9 + m2_15 * m1_13,
                    m2_12 * m1_2 + m2_13 * m1_6 + m2_14 * m1_10 + m2_15 * m1_14,
                    m2_12 * m1_3 + m2_13 * m1_7 + m2_14 * m1_11 + m2_15 * m1_15]

        return self


    def get_inverse(self):

        """Returns the inverse (matrix with the opposite effect) of this
        matrix."""


        i = self.values

        i0,  i1,  i2,  i3, \
        i4,  i5,  i6,  i7, \
        i8,  i9,  i10, i11, \
        i12, i13, i14, i15 = i

        negpos=[0., 0.]
        temp = i0 * i5 * i10
        negpos[temp > 0.] += temp

        temp = i1 * i6 * i8
        negpos[temp > 0.] += temp

        temp = i2 * i4 * i9
        negpos[temp > 0.] += temp

        temp = -i2 * i5 * i8
        negpos[temp > 0.] += temp

        temp = -i1 * i4 * i10
        negpos[temp > 0.] += temp

        temp = -i0 * i6 * i9
        negpos[temp > 0.] += temp

        det_1 = negpos[0]+negpos[1]

        if (det_1 == 0.) or (abs(det_1 / (negpos[1] - negpos[0])) < \
                             (2. * 0.00000000000000001) ):
            raise Exception("notivertable", "This Matrix44 can not be inverted")

        det_1 = 1. / det_1

        ret = Matrix(*[ (i5*i10 - i6*i9)*det_1,
                  -(i1*i10 - i2*i9)*det_1,
                   (i1*i6 - i2*i5 )*det_1,
                   0.0,
                  -(i4*i10 - i6*i8)*det_1,
                   (i0*i10 - i2*i8)*det_1,
                  -(i0*i6 - i2*i4)*det_1,
                   0.0,
                  (i4*i9 - i5*i8 )*det_1,
                  -(i0*i9 - i1*i8)*det_1,
                   (i0*i5 - i1*i4)*det_1,
                   0.0,
                   0.0, 0.0, 0.0, 1.0 ])

        m = ret.values
        m[12] = - ( i12 * m[0] + i13 * m[4] + i14 * m[8] )
        m[13] = - ( i12 * m[1] + i13 * m[5] + i14 * m[9] )
        m[14] = - ( i12 * m[2] + i13 * m[6] + i14 * m[10] )

        return ret

    def get_translate(self):
        return vec.Vector(*self.values[12:15])

    def set_translate(self, values):
        if not len(values):
            raise Exception('Three float values are required to set translate')
        elif not all(isinstance(x, float) for x in values):
            raise Exception('Matrix values must be type: float, not : %s' % [type(x) for x in values])
        self.values[12] = values[0]
        self.values[13] = values[1]
        self.values[14] = values[2]

    def set_scale(self, values):
        if not len(values):
            raise Exception('Three float values are required to set scale')
        elif not all(isinstance(x, float) for x in values):
            raise Exception('Matrix values must be type: float, not : %s' % [type(x) for x in values])
        self.values[0] = values[0]
        self.values[5] = values[1]
        self.values[10] = values[2]

    def get_scale(self):
        return vec.Vector(self.values[0], self.values[5], self.values[10])

    def zero_rotate(self):
        self.values[1] = 0.0
        self.values[2] = 0.0
        self.values[4] = 0.0
        self.values[6] = 0.0

    def get_rotate(self, rotate_order='xyz'):

        x_vec = vec.Vector(*self.values[0:3]).normalize()
        y_vec = vec.Vector(*self.values[4:7]).normalize()

        z_cross_vec = x_vec.cross(y_vec).normalize()
        y_cross_vec = z_cross_vec.cross(x_vec).normalize()
        x_cross_vec = y_cross_vec.cross(z_cross_vec).normalize()

        if rotate_order in ('xyz', 0):
            return vec.Vector(*[math.degrees(math.atan2(y_cross_vec[2], z_cross_vec[2])),
                math.degrees(math.asin(-x_cross_vec[2])),
                math.degrees(math.atan2(x_cross_vec[1], x_cross_vec[0]))])
        elif rotate_order in ('yzx', 1):
            return vec.Vector(*[math.degrees(math.atan2(z_cross_vec[0], x_cross_vec[0])),
                math.degrees(math.asin(-y_cross_vec[0])),
                math.degrees(math.atan2(y_cross_vec[2], y_cross_vec[1]))])
        elif rotate_order in ('zxy', 2):
            return vec.Vector(*[math.degrees(math.atan2(x_cross_vec[1], y_cross_vec[1])),
                math.degrees(math.asin(-z_cross_vec[1])),
                math.degrees(math.atan2(z_cross_vec[0], z_cross_vec[2]))])
        elif rotate_order in ('xzy', 3):
            return vec.Vector(*[math.degrees(math.atan2(-z_cross_vec[1], y_cross_vec[1])),
                math.degrees(math.asin(x_cross_vec[1])),
                math.degrees(math.atan2(-x_cross_vec[2], x_cross_vec[0]))])
        elif rotate_order in ('yxz', 4):
            return vec.Vector(*[math.degrees(math.atan2(-x_cross_vec[2], z_cross_vec[2])),
                math.degrees(math.asin(y_cross_vec[2])),
                math.degrees(math.atan2(-y_cross_vec[0], y_cross_vec[1]))])
        elif rotate_order in ('zyx', 5):
            return vec.Vector(*[math.degrees(math.atan2(-y_cross_vec[0], x_cross_vec[0])),
                math.degrees(math.asin(z_cross_vec[0])),
                math.degrees(math.atan2(-z_cross_vec[1], z_cross_vec[2]))])
        else:
            valid_values = ('xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx')
            raise ValueError("'rotateOrder' value [{0}]	 invalid! Valid values are: 0 - 5, {1}.".format(
                rotate_order, valid_values, conjunction='and'))


def triangulate_matrix(p1, p2, up_vector=[0, 1, 0]):
    start = vec.Vector(*p1)
    end = vec.Vector(*p2)
    difference = end - start
    aim_vector = difference.normalize()
    side_vector = aim_vector.cross(up_vector)
    up_vector = side_vector.cross(aim_vector)
    m = []
    m.extend([aim_vector[0], aim_vector[1], aim_vector[2], 0])
    m.extend([up_vector[0], up_vector[1], up_vector[2], 0])
    m.extend([side_vector[0], side_vector[1], side_vector[2], 0])
    m.extend([p1[0], p1[1], p1[2], 1])
    return Matrix(*m)

























    '''
    def getScale(self):
        x_vec = vec.Vector(*self.values[0:3]).normalize()
        y_vec = vec.Vector(*self.values[4:7]).normalize()
        z_vec = vec.Vector(*self.values[8:11]).normalize()

        xy_cross_vec = x_vec.cross(y_vec).normalize()


        xyCrossNormVec = vector.norm(vector.cross(xAxisVec, yAxisVec))
        xAxisNormVec = vector.norm(xAxisVec)
        xyCrossXVec = vector.cross(xyCrossNormVec, xAxisNormVec)
        xScale = vector.mag(xAxisVec)
        yScale = vector.dot(xyCrossXVec, yAxisVec)
        zScale = vector.dot(xyCrossNormVec, zAxisVec)

        return [xScale, yScale, zScale]

    def getShear(matrix):

        yAxis_vec = (matrix[4], matrix[5], matrix[6])
        zAxis_vec = (matrix[8], matrix[9], matrix[10])

        xAxis_unit_vec = vector.norm((matrix[0], matrix[1], matrix[2]))

        xyAxis_cross_unit_vec = vector.norm(vector.cross(xAxis_unit_vec, vector.norm(yAxis_vec)))
        xzAxis_cross_unit_vec = vector.cross(xyAxis_cross_unit_vec, xAxis_unit_vec)

        return [(vector.dot(xAxis_unit_vec, yAxis_vec) / vector.dot(xzAxis_cross_unit_vec, yAxis_vec)),
            (vector.dot(xAxis_unit_vec, zAxis_vec) / vector.dot(xyAxis_cross_unit_vec, zAxis_vec)),
            (vector.dot(xzAxis_cross_unit_vec, zAxis_vec) / vector.dot(vector.cross(xAxis_unit_vec,
                                                                                    xzAxis_cross_unit_vec), zAxis_vec))]
    '''