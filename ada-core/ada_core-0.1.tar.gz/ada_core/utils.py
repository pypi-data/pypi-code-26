"""
Author: qiacai
"""

from ada_core.data.time_series import TimeSeries
from ada_core.data.entry import Entry


def isfloat(x):
    try:
        float(x)
        return True
    except ValueError or TypeError:
        return False


def isbool(x):
    try:
        strValue = str(x)
        if strValue.lower() in ("true", "yes", "t", "1", "y", "false", "no", "f", "0", "n"):
            return True
        else:
            return False
    except ValueError or TypeError:
        return False


def str2bool(x):
    if isbool(x):
        return str(x).lower() in ("true", "yes", "t", "1", "y")
    else:
        return False


def isSimpleValue(x):
    try:
        if isinstance(x, Entry) or isinstance(x, TimeSeries) or isbool(x) or isfloat(x) or str.isdecimal(str(x)):
            return True
        else:
            return False
    except TypeError or ValueError:
        return False