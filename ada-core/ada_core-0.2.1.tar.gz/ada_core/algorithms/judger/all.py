"""
Author: qiacai
"""

from ada_core.algorithms.judger import *


base_pool = {
    "base_binary_judger": base_binary_judger.BaseBinaryJudger
}


judgers_pool = {
    "=": base_binary_judger.EqualBinaryJudger,
    "equal": base_binary_judger.EqualBinaryJudger,
    ">": base_binary_judger.GreaterThanBinaryJudger,
    "greater_than": base_binary_judger.GreaterThanBinaryJudger,
    ">=": base_binary_judger.GreaterThanOrEqualBinaryJudger,
    "greater_than_or_equal": base_binary_judger.GreaterThanOrEqualBinaryJudger,
    "<": base_binary_judger.LessThanBinaryJudger,
    "less_than": base_binary_judger.LessThanBinaryJudger,
    "<=": base_binary_judger.LessThanOrEqualBinaryJudger,
    "less_than_or_equal": base_binary_judger.LessThanOrEqualBinaryJudger

}
