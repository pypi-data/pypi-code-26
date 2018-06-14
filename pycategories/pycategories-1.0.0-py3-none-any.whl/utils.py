from functools import reduce


def funcall(f, *args):
    return f(*args)


def unit(x):
    """identity function"""
    return x


def flip(f):
    """Return a function that reverses the arguments it's called with"""
    return lambda x, y: f(y, x)


def compose(*fs):
    """
    Return a function that is the composition of the functions in fs.
    All functions in f must take a single argument.

    Ex:
    compose(f, g)(x) == f(g(x))

    Adapted from this StackOverflow answer:
    https://stackoverflow.com/a/34713317
    """
    return lambda x: reduce(flip(funcall), reversed(fs), x)
