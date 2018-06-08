# Forecasting Confidence Interval.

from .forecasters import forecaster as fc
from .forecasters import CIFrame
from .logger import *


__all__ = ['forecast_ci']


def forecast_ci(data, forecaster, fn=1, spices=None):
    """ Forecasts confidence intervals.

    :param data: Iterable rows
    :param forecaster: name of a registered forecaster
    :param fn: number of forecasting time units
    :param spices: spices of the forecaster
    :return: Iterable CIFrame objects
    """
    return _forecast_ci(data, forecaster, fn, spices)


def _forecast_ci(data, forecaster, fn=1, spices=None):
    """ Forecasts confidence intervals.

    :param data: Iterable rows
    :param forecaster: name of a registered forecaster
    :param fn: number of forecasting time units
    :param spices: spices of the forecaster
    :return: list of CIFrame objects
    """
    logger.info("Forecaster: %s, fn: %d" % (forecaster, fn))
    if not spices:
        spices = ()

    result = []
    for row in data:
        forecaster_output = fc.getattr(forecaster)(row, fn, *spices)
        if _is_forecaster_valid(forecaster_output):
            result.append(forecaster_output)
        else:
            raise Exception('Forecaster is invalid. forecaster = %s\n '
                            'A forecaster must returns a CIFrame object!' % forecaster)

    return result


def _is_forecaster_valid(forecaster_output):
    return True if isinstance(forecaster_output, CIFrame) else False