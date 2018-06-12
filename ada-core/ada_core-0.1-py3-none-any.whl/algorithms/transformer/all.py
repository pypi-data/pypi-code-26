"""
Author: qiacai
"""

from ada_core.algorithms.transformer import *


transformers_pool = {
    "seasonal_decompose": seasonal_decompose.SeasonalDecompose,
    "value_offset":basic_transformers.ValueOffset,
    "time_offset": basic_transformers.TimeOffset,
    "standard_normalization": basic_transformers.StandardNormalization,
    "scale_normalization": basic_transformers.ScaleNormalization
}