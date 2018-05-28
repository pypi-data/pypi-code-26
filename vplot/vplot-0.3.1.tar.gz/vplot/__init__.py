#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, \
     unicode_literals

__version__ = "0.3.1"
__author__ = "Rodrigo Luger (rodluger@uw.edu)"
__copyright__ = "Copyright 2018 Rodrigo Luger"

# Was vplot imported from setup.py?
try:
    __VPLOT_SETUP__
except NameError:
    __VPLOT_SETUP__ = False

# This is a regular vplot run
if not __VPLOT_SETUP__:

    # Set up the matplotlib stylesheet
    import os
    import matplotlib.pyplot as pl
    pl.style.use(os.path.join(os.path.dirname(
                 os.path.abspath(__file__)),
        'vplot.mplstyle'))

    # Import main stuff
    from . import plot, quickplot, utils, log
    from .utils import GetOutput
    from .plot import plot, show, savefig, colors, make_pretty
