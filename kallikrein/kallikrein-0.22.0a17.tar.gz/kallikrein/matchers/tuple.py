from typing import TypeVar, Collection, Tuple, Any, Generic

from amino import Boolean, List, L, Lists
from amino.boolean import false

from kallikrein.matcher import Predicate, Nesting, BoundMatcher, matcher_f, ChainMatcher, StrictMatcher
from kallikrein.match_result import MatchResult, ContainsMatchResult, ForAllMatchResult

A = TypeVar('A')
B = TypeVar('B')


class Tupled:
    pass


class PredTupled(Predicate[Tuple, int]):
    pass


class NestTupled(Nesting):
    pass


class BadTupledMatchers(MatchResult):

    @property
    def success(self) -> Boolean:
        return false

    @property
    def message(self) -> List[str]:
        return List(f'tupled matchers have invalid length')


def eval_tupled(exp: Tuple, matchers: Tuple[BoundMatcher, ...]) -> ForAllMatchResult:
    results = Lists.wrap(matchers).zip(Lists.wrap(exp)).map2(lambda m, e: m.evaluate(e))
    return ForAllMatchResult('foo', exp, results)


class TupledMatchers(BoundMatcher[Tuple]):

    def __init__(self, matchers: Tuple[BoundMatcher, ...]) -> None:
        self.matchers = matchers

    def evaluate(self, exp: Tuple) -> MatchResult[Tuple]:
        return (
            BadTupledMatchers()
            if len(exp) != len(self.matchers) else
            eval_tupled(exp, self.matchers)
        )


class ChainMatcherTupled(ChainMatcher[Tuple[BoundMatcher, ...]], tpe=Tupled):

    def chain(self, match: StrictMatcher, other: Tuple[BoundMatcher, ...]) -> BoundMatcher:
        return match & TupledMatchers(other)


class PredTupledTuple(PredTupled, tpe=object):

    def check(self, exp: Tuple, target: int) -> Boolean:
        return Boolean(isinstance(exp, tuple) and len(exp) == target)


class NestTupledCollection(NestTupled, tpe=object):

    def match(self, exp: Collection[A], target: BoundMatcher) -> List[MatchResult[B]]:
        return List.wrap([target.evaluate(e) for e in exp])

    def wrap(self, name: str, exp: Collection[A], nested: List[MatchResult[B]]) -> MatchResult[A]:
        return ContainsMatchResult(name, exp, nested)


def msg(success: bool, exp: Any, target: int) -> List[str]:
    return List(
        f'`{exp}` is a tuple of size {target}'
        if success else
        f'`{exp}` is not a tuple of size {target}'
        if isinstance(exp, tuple) else
        f'`{exp}` is not a tuple'
    )


be_tuple = tupled = matcher_f(Tupled, msg, PredTupled, NestTupled)

__all__ = ('tupled', 'be_tuple')
