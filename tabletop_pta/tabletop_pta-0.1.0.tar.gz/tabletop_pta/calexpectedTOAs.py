# -*- coding: utf-8 -*-
from __future__ import division, print_function
import numpy as np

def calexpectedTOAs(t0, n0, Np, Tp):

    '''
    calculated expected TOAs given reference TOA and estimated pulse period
    '''

    expectedTOAs = t0 + np.transpose(np.linspace((1-n0)*Tp, (Np-n0)*Tp, Np));

    return expectedTOAs
