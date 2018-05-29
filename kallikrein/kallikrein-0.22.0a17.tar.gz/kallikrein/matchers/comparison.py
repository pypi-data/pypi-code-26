import abc
import operator
from typing import Tuple, Callable, Generic, TypeVar
from numbers import Number

from kallikrein.match_result import MatchResult, SimpleMatchResult, BadNestedMatch
from kallikrein.matcher import Matcher, BoundMatcher
from amino import Boolean, L, _, List

A = TypeVar('A')


class Comparison(Generic[A], Matcher[A]):

    @abc.abstractproperty
    def operator(self) -> Callable[[A, A], Boolean]:
        ...

    @abc.abstractproperty
    def operator_reprs(self) -> Tuple[str, str]:
        ...

    def match(self, exp: A, target: A) -> MatchResult[A]:
        result = Boolean(self.operator(exp, target))
        op_s, op_f = self.operator_reprs
        op = op_s if result else op_f
        message = '{} {} {}'.format(exp, op, target)
        return SimpleMatchResult(result, List(message))

    def match_nested(self, exp: A, target: BoundMatcher) -> MatchResult[A]:
        return BadNestedMatch(self)


class NumberComparison(Comparison[Number]):

    def __init__(self, op: Callable[[Number, Number], bool], op_s: str, op_f: str) -> None:
        self.op = op
        self.op_s = op_s
        self.op_f = op_f

    @property
    def operator(self) -> Callable[[Number, Number], Boolean]:
        return L(self.op)(_, _) >> Boolean

    @property
    def operator_reprs(self) -> Tuple[str, str]:
        return self.op_s, self.op_f


def number_comparison(op: Callable[[Number, Number], bool], op_s: str, op_f: str) -> Matcher[Number]:
    return NumberComparison(op, op_s, op_f)


equal = number_comparison(operator.eq, '==', '!=')
eq = equal

not_equal = number_comparison(operator.ne, '!=', '==')
ne = not_equal

greater_equal = number_comparison(operator.ge, '>=', '<')
ge = greater_equal

greater = number_comparison(operator.gt, '>', '<=')
gt = greater

less_equal = number_comparison(operator.le, '<=', '>')
le = less_equal

less = number_comparison(operator.lt, '<', '>=')
lt = less

__all__ = ('equal', 'greater_equal', 'eq', 'ge', 'greater', 'gt', 'less_equal', 'le', 'less', 'lt')
