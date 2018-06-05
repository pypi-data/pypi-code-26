""" Vector class
"""

# standard modules
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

__all__ = ['Vector']

__date__ = '08042017'
__version__ = '0.1.0'
__author__ = 'J. G. Chen'
__email__ = 'cjgls@pku.edu.cn'

import numpy as np

from boutpy.boutdata.field import Field


class Vector(object):
    def __init__(self, x=None, y=None, z=None, covariant=True):
        raise NotImplementedError("Further Works Required!")
        self.covariant = covariant
        self.x = Field(x)
        self.y = Field(y)
        self.z = Field(z)

        if self.x.shape != self.y.shape:
            raise TypeError("components of a Vector must be in same shape, "
                            "x={}, y={}".format(self.x.shape, self.y.shape))
        elif (self.z is not None) and (self.z.shape != self.x.shape):
            raise TypeError("components of a Vector must be in same shape, "
                            "x:{}, z:{}".format(self.x.shape, self.z.shape))

    def __repr__(self):
        prefixstr = self.__class__.__name__ + ' '
        xstr = np.array2string(self.x.view(np.ndarray), separator=',',
                               prefix=prefixstr)
        ystr = np.array2string(self.y.view(np.ndarray), separator=',',
                               prefix=prefixstr)
        if self.z is not None:
            zstr = np.array2string(self.z.view(np.ndarray), separator=',',
                                   prefix=prefixstr)
            return "{}<{}, {}, {}>".format(prefixstr, xstr, ystr, zstr)
        else:
            return "{}<{}, {}>".format(prefixstr, xstr, ystr)

    def toContravariant(self):
        if self.covariant:
            self.covariant = False

    def toCovariant(self):
        if not self.covariant:
            self.covariant = True
