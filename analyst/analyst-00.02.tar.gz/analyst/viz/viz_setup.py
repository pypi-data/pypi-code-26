#!/usr/bin/env python3
# coding: utf-8

"""
    Setting up Python data visualization environment
    ver. 01 prod

 -----------------------------------------------------------------------------
                                                             hs@uchicago.edu
                                                                June 1, 2018


Initialize `matplotlib` and `seaborn` plotting environment for Jupyter
notebook or iPython. Provide some helper functions.

Example usage:
    from analyst import viz
""";


import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns


# The import below do not work in a Jupyter notebook development environment
# Will raise ValueError: attempted relative import beyond top-level package
# Hence, this cell is freezed in Jupyter notebook
from ..utils.logging_init import in_ipynb, info


if in_ipynb():
    get_ipython().magic('matplotlib inline')
    info('Jupyter notebook environment detected. Set `matplotlib` to '
         '`inline` mode')


def setup(style="ticks", font="sans-serif", font_scale=1.2):
    """
    """
    sns.set(style=style, font=font, font_scale=font_scale, color_codes=True)

