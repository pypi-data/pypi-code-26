"""
Author: qiacai
"""

from ada_core.algorithms.calculator import *

base_pool = {
    "base_ts_numeric_calculator": base_ts_numeric_calculator.BaseTsNumericCalculator
}


calculators_pool = {
    "mean": base_ts_numeric_calculator.Mean,
    "median": base_ts_numeric_calculator.Median,
    "max": base_ts_numeric_calculator.Max,
    "min": base_ts_numeric_calculator.Min,
    "percentile": base_ts_numeric_calculator.Percentile,
    "std": base_ts_numeric_calculator.Std,
    "mad": base_ts_numeric_calculator.Mad,
    "count": base_ts_numeric_calculator.Count,
    "sum": base_ts_numeric_calculator.Sum
}