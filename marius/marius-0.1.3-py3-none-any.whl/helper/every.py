import time
import itertools
from marius import TimeLine, Task


def every(interval):
    """
    build a generator of unix time
    :param interval:
        interval of each execution, unit: seconds
    :return: a generator of unix timestamp
    """

    if not isinstance(interval, (int, float)):
        raise ValueError('interval must be a number')

    sequence = (time.time() + interval for _ in itertools.count(1))

    def wrapper(func):
        TimeLine().add(Task(sequence, func))

    return wrapper
