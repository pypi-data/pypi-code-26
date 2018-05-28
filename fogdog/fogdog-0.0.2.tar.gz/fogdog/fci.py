# Forecasting Confidence Interval.

from .forecasters import forecaster as fc
from .forecasters import CIFrame
from .logger import *


__all__ = ['forecast_ci']


def forecast_ci(data, forecaster, fn=1):
    """ Forecasts confidence intervals.

    :param data: Iterable rows
    :param forecaster: name of a registered forecaster
    :param fn: number of forecasting time units
    :return: Iterable CIFrame objects
    """
    logger.info("Forecaster: %s, fn: %d" % (forecaster, fn))
    for row in data:
        forecaster_output = fc.getattr(forecaster)(row, fn)
        if _is_forecaster_valid(forecaster_output):
            yield forecaster_output
        else:
            raise Exception('Forecaster is not valid. forecaster = %s\n '
                            'A forecaster must returns a CIFrame object!' % forecaster)


def _is_forecaster_valid(forecaster_output):
    return True if isinstance(forecaster_output, CIFrame) else False
