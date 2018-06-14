from functools import partial

from categories import instances
from categories.utils import compose, unit


__instances = {}
get_instance = instances.make_getter(__instances, 'Functor')
_add_instance = instances.make_adder(__instances)
undefine_instance = instances.make_undefiner(__instances)


class Functor:
    def __init__(self, fmap):
        self.fmap = fmap


def instance(type, fmap):
    instance = Functor(fmap)
    _add_instance(type, instance)
    return instance


def fmap(f, x):
    instance = get_instance(type(x))
    return instance.fmap(f, x)


def identity_law(x):
    """
    fmap id == id
    """
    return fmap(unit, x) == unit(x)


def composition_law(f, g, x):
    """
    fmap (g . f) == fmap g . fmap f
    """
    composed_funcs = compose(g, f)
    composed_fmaps = compose(partial(fmap, g), partial(fmap, f))
    return fmap(composed_funcs, x) == composed_fmaps(x)
