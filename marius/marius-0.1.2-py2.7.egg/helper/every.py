import time
import itertools


def every(interval):
    """
    build a generator of unix time
    :param interval:
        interval of each execution, unit: seconds
    :return: a generator of unix timestamp
    """

    if not isinstance(interval, (int, float)):
        raise ValueError('interval must be a number')

    return (time.time() + interval for _ in itertools.count(1))
