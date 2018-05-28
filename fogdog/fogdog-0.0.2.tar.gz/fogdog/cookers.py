from .logger import *


__all__ = ['cooker']


# --------------------------------
# Decorator
# For registering cookers
# --------------------------------
class Cooker(object):

    def __init__(self):
        self._cookers = {}

    def __call__(self, name):
        def wrapper(func):
            self._cookers[name] = func
            return func
        return wrapper

    def getattr(self, name):
        if name in self._cookers.keys():
            return self._cookers[name]
        else:
            raise ValueError('Cooker is not registered! name = %s' % name)


cooker = Cooker()
# --------------------------------


# --------------------------------
# Registered cookers.
# --------------------------------

@cooker('MoveSum')
def move_sum(row, k=1, step=1):
    if k == 1 and step == 1:
        return row
    m = (len(row) - k) // step + 1
    return [sum((row[i * step: i * step + k])) for i in range(m)]
