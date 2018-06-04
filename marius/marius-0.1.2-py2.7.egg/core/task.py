from functools import partial


class Task(object):
    def __init__(self, sequence, func, *args, **kwargs):
        """
        wrap a function into a TaskTask
        :param sequence:
            a generator of unix time
        :param func:
            function that to be run
        :param args,kwargs:
            func's args and kwargs
        """
        if not callable(func):
            raise ValueError('func must be callable')

        self.time = next(sequence)
        self.sequence = sequence
        self.func = partial(func, *args, **kwargs)

    def __lt__(self, other):
        if not isinstance(other, Task):
            raise TypeError('only TaskTask object can be compare.')

        return self.time < other.time
