#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is the unittest of the kriging module.
"""
from __future__ import division, absolute_import, print_function

import unittest
import numpy as np
from gstools.krige import Kriging


class TestKriging(unittest.TestCase):
    def setUp(self):
        self.x_grid = np.arange(0.0, 5., 0.5)
        self.y_grid = np.arange(0.0, 5., 0.5)

    def test_OK_1d(self):
        x_grid = np.linspace(0., 5., 100)
        truth = np.sin(3*x_grid) * .5 * np.cos(.5*x_grid) * .2
        idx = np.array((3, 10, 30, 35, 50, 70, 90))
        pos_data = x_grid[idx]
        data = truth[idx]

        k = Kriging(1, pos_data, data)
        Z, var = k.ordinary(x_grid, model='linear', slope=1.18879745e-01,
                               nugget=5.89805982e-17)

    #def test_OK_fit_1d(self):
    #    x_grid = np.linspace(0., 5., 100)
    #    truth = np.sin(3*x_grid) * .5 * np.cos(.5*x_grid) * .2
    #    idx = np.array((3, 10, 30, 35, 50, 70, 90))
    #    #idx = np.array((1, 3, 9))
    #    pos_data = x_grid[idx]
    #    data = truth[idx]

    #    k = Kriging(1, pos_data, data)
    #    Z, var = k.ordinary(x_grid, model='linear')


    #    import matplotlib.pyplot as pt
    #    pt.plot(x_grid, truth)
    #    pt.scatter(pos_data, data, color='r')
    #    pt.plot(x_grid, Z, linestyle='--', color='g')
    #    pt.show()


    def test_OK_struct_2d(self):
        data_x = np.array((0.3, 1.9, 1.1, 3.3, 4.7))
        data_y = np.array((1.2, 0.6, 3.2, 4.4, 3.8))
        data_v = np.array((0.47, 0.56, 0.74, 1.47, 1.74))
        k = Kriging(2, (data_x, data_y), data_v)
        Z, var = k.ordinary((self.x_grid, self.y_grid),
                            model='linear', slope=1.18879745e-01,
                            nugget=5.89805982e-17)
        #print(Z[0,0], Z[-1,1])
        #print(var[0,0], var[-1,1])


if __name__ == '__main__':
    unittest.main()
