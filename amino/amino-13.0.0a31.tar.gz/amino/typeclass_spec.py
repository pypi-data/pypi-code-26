from typing import Callable, TypeVar, Any, Generic

from amino.test.spec_spec import Spec
from amino.typeclass.typeclass import instance
from amino.typeclass.functor import Functor, fmap

A = TypeVar('A')
B = TypeVar('B')

_A = TypeVar('_A')

# class Maybe(Generic[_A]):
#     pass


# class Just(Maybe[_A]):

#     def __init__(self, value: _A) -> None:
#         self.value = value


# class _Nothing(Maybe[A]):
#     pass


# Nothing: Maybe[Any] = _Nothing()


def fmap_maybe(f: Callable[[A], B], fa: Maybe[A]) -> Maybe[B]:
    return Just(f(fa.value)) if isinstance(fa, Just) else Nothing


maybe_instance = instance(Functor, Maybe, fmap=fmap_maybe)


class _TypeclassSpec(Spec):

    def fmap(self) -> None:
        print(fmap(lambda a: a + 1)(Just(1)))


__all__ = ('_TypeclassSpec',)
