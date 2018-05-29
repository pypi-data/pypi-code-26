#!/usr/bin/env python3
"""
Import, compute and plot Power Spectral Densities

Use this tool to quickly compute, or plot PSDs from data contained
in one or multiple files, using parametrized Welch method.

Jean-Baptiste Bayle, APC/CNRS/CNES, 20/03/2017.
"""

from .psd import Series
from .psd import SpectralEstimator
