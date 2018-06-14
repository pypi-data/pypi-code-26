from categories import applicative, functor, mappend
from categories import monad, monoid


class Maybe:
    def __init__(self, type, value=None):
        self.type = type
        if self.type == 'Just':
            self.value = value

    def __repr__(self):
        return ('Nothing' if self.type == 'Nothing' else
                'Just({})'.format(repr(self.value)))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return (self.type == other.type and
                    self.__dict__ == other.__dict__)
        else:
            return False

    @classmethod
    def just(cls, value):
        return cls('Just', value)

    @classmethod
    def nothing(cls):
        return cls('Nothing')


Just = Maybe.just
Nothing = Maybe.nothing


def _mappend(a, b):
    if a == Nothing():
        return b
    elif b == Nothing():
        return a
    else:
        return Just(mappend(a.value, b.value))


def _fmap(f, x):
    return Just(f(x.value)) if x.type == 'Just' else Nothing()


def _apply(f, x):
    if f.type == 'Just' and x.type == 'Just':
        return Just(f.value(x.value))
    else:
        return Nothing()


def _bind(m, f):
    if m == Nothing():
        return Nothing()
    else:
        return f(m.value)


functor.instance(Maybe, _fmap)
monoid.instance(Maybe, lambda: Nothing(), _mappend)
applicative.instance(Maybe, Just, _apply)
monad.instance(Maybe, Just, _bind)
