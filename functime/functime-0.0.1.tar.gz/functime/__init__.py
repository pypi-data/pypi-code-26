"""
This moudle provides a simple way to time a function.
"""
name = 'functime'

__all__ = ['func_time']

import time
import functools


def time_format(run_time):
    if run_time < 10**-3:
        time_str = str(round(run_time*(10**6), 6)) + 'us'
    elif run_time < 1:
        time_str = str(round(run_time*(10**3), 4)) + 'ms'
    else:
        time_str = str(round(run_time.round(2), 2)) + 's'
    return time_str


def timer(func, times=1):
    """
    Run a function in loop, the number of repeats is given by argument times.
    Return the total time in seconds.
    This function can't receive any argument of func. Use func from functools.partial instead.
    """
    start = time.time()
    for i in range(times):
        func()
    run_time = time.time() - start
    return run_time


def func_time(func, *args, **kwargs):
    """
    Recommended function.
    Time func with its arguments followed by func.
    Call timer(func, times) repeatedly with times set to (10, 100, 1000, ...) so that the total time >= 0.2.
    Print average run time with readable format.
    """
    times = 1
    all_time = timer(functools.partial(func, *args, **kwargs), times)
    while all_time < 0.2:
        times *= 10
        all_time = timer(functools.partial(func, *args, **kwargs), times)
    time_str = time_format(all_time / times)
    print(func.__name__, 'AVG(%d): %s' % (times, time_str))
