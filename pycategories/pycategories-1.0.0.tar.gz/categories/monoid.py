from functools import reduce

from categories import instances


__instances = {}
get_instance = instances.make_getter(__instances, 'Monoid')
_add_instance = instances.make_adder(__instances)
undefine_instance = instances.make_undefiner(__instances)


class Monoid:
    def __init__(self, mempty, mappend):
        self.mempty = mempty
        self.mappend = mappend


def instance(type, mempty, mappend):
    instance = Monoid(mempty, mappend)
    _add_instance(type, instance)
    return instance


def mappend(*xs):
    instance = get_instance(type(xs[0]))
    return reduce(instance.mappend, xs)


def mempty(type):
    instance = get_instance(type)
    return instance.mempty()


def associativity_law(x, y, z):
    """
    (x <> y) <> z = x <> (y <> z)
      where (<>) = mappend
    """
    return mappend(mappend(x, y), z) == mappend(x, mappend(y, z))


def identity_law(x):
    """
    Assert left and right identity laws:

    mempty <> x = x
    x <> mempty = x
      where (<>) = mappend
    """
    return (mappend(x, mempty(type(x))) == x and
            mappend(mempty(type(x)), x) == x)
