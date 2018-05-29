from typing import TypeVar, Generic, Callable

from amino.util.exception import format_exception

from kallikrein.matcher import Matcher, BoundMatcher
from kallikrein.match_result import MatchResult, BadNestedMatch, SimpleMatchResult
from kallikrein import Expectation
from kallikrein.util.string import red
from kallikrein.expectation import ExpectationResult

A = TypeVar('A')
B = TypeVar('B')
success_tmpl = '`{}` matches with `{}`'
failure_tmpl = '`{}` does not match with `{}`'


def match_with_fatal(exc: Exception) -> MatchResult[B]:
    return SimpleMatchResult(False, format_exception(exc).cons(red('exception in `match_with`')))


def match_with_result(result: ExpectationResult) -> MatchResult[B]:
    return SimpleMatchResult(result.success, result.report_lines)


class MatchWith(Generic[A, B], Matcher[B]):

    def match(self, exp: A, target: Callable[[A], Expectation[B]]) -> MatchResult[B]:
        bound = target(exp)
        return bound.evaluate.attempt.cata(match_with_fatal, match_with_result)

    def match_nested(self, exp: A, target: BoundMatcher) -> MatchResult[B]:
        return BadNestedMatch(target)


match_with = MatchWith()

__all__ = ('match_with',)
