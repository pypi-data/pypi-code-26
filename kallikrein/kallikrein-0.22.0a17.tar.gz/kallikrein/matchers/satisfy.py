from typing import TypeVar, Generic, Callable, Any
from collections.abc import Sequence as SequenceABC

from amino import Boolean, L, _

from kallikrein.matcher import Predicate, matcher, NestingUnavailable

A = TypeVar('A')
B = TypeVar('B')


class SatisfyPredicate:
    pass


class PredSatisfyPredicate(Generic[A], Predicate[A, Callable[[A], bool]]):
    pass


is_seq = L(issubclass)(_, SequenceABC)


class PredSatisfyPredicateAny(Generic[A], PredSatisfyPredicate[A], tpe=object):

    def check(self, exp: A, target: Callable[[A], bool]) -> Boolean:
        return Boolean(target(exp))


success = '`{}` satisfies `{}`'
failure = '`{}` does not satisfy `{}`'
satisfy = matcher(SatisfyPredicate, success, failure, PredSatisfyPredicate, NestingUnavailable)


__all__ = ('satisfy',)
