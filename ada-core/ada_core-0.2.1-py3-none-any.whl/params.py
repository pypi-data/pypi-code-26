"""
Author: qiacai
"""


"""
Params for algorithms
"""

params_algorithm_calculator_percentile = {
    "percent": {"type": int, "optional": False, "range": "0 ~ 100"}
}

params_algorithm_transformer_offset_value = {
    "offset_value": {"type": float, "optional": True, "range": "-infinite ~ +infinite"}
}

params_algorithm_transformer_offset_time = {
    "offset_time": {"type": int, "optional": True, "range": "-current value ~ +infinite"}
}

params_algorithm_transformer_smoothing_factor = {
    "smoothing_factor": {"type": float, "optional": False, "range": "0 ~ 1"}
}

params_algorithm_transformer_seasonal_decompose = {
    "freq": {"type": int, "optional": True, "range": "0 ~ +infinite"},
    "trend_only": {"type": bool, "optional": True, "range": "(True, False)"},
    "is_fillna": {"type": bool, "optional": True, "range": "(True, False)"}
}


