# -*- coding: utf-8 -*-
from __future__ import division, print_function
import numpy as np

def calcorrcoeff(x,y):

    '''
    calculate correlation coefficient of x and y, relative to x, y, or z
    '''

    rhox = np.sum(x*y)/np.sum(x*x)
    rhoy = np.sum(x*y)/np.sum(y*y)
    rhoxy = np.sum(x*y)/np.sqrt(np.sum(x*x) * np.sum(y*y))

    return rhox, rhoy, rhoxy
