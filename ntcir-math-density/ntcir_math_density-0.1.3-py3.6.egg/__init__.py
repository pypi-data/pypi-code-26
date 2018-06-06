"""
The NTCIR Math Density Estimator package uses NTCIR-10 Math, NTCIR-11 Math-2, and NTCIR-12 MathIR
datasets to compute density, and probability estimators.
"""

from .estimator import get_judged_identifiers, get_all_positions, get_estimators, get_estimates
from .view import plot_estimates


__author__ = "Vit Novotny"
__version__ = "0.1.3"
__license__ = "MIT"
