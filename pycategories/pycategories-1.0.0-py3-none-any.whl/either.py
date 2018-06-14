from categories import applicative, functor, monad


class Either:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return '{}({})'.format(self.type, repr(self.value))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return (self.type == other.type and
                    self.__dict__ == other.__dict__)
        else:
            return False

    @classmethod
    def left(cls, value):
        return cls('Left', value)

    @classmethod
    def right(cls, value):
        return cls('Right', value)


Left = Either.left
Right = Either.right


def _fmap(f, x):
    if x.type == 'Right':
        return Right(f(x.value))
    else:
        return x


def _apply(f, x):
    if f.type == 'Right' and x.type == 'Right':
        return Right(f.value(x.value))
    elif f.type == 'Left':
        return f
    elif x.type == 'Left':
        return x


def _bind(m, f):
    """
    (>>=) :: Monad m => m a -> (a -> m b) -> m b
    """
    if m.type == 'Right':
        return f(m.value)
    else:
        return m


functor.instance(Either, _fmap)
applicative.instance(Either, Right, _apply)
monad.instance(Either, Right, _bind)
