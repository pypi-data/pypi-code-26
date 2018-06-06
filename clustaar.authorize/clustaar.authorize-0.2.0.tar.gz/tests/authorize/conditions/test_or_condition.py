import pytest
from clustaar.authorize.conditions_combinations import AndCondition, OrCondition
from clustaar.authorize.conditions import FalseCondition, TrueCondition


@pytest.fixture
def invalid():
    return FalseCondition()


@pytest.fixture
def valid():
    return TrueCondition()


class TestCall(object):
    def test_returns_false_all_conditions_are_invalid(self, invalid):
        condition = OrCondition([invalid, invalid, invalid])
        assert not condition({})

    def test_returns_true_if_one_condition_is_valid(self, invalid, valid):
        condition = OrCondition([invalid, valid, invalid])
        assert condition({})

    def test_returns_true_if_complex_expression_is_valid(self, invalid, valid):
        condition = (valid & valid) | invalid & valid & valid | invalid
        assert condition({})

    def test_returns_false_if_complex_expression_is_invalid(self, invalid, valid):
        condition = (valid & invalid) | invalid & valid & valid | invalid
        assert not condition({})


class TestOr(object):
    def test_returns_self_if_other_is_a_condition(self, valid):
        condition = valid | valid
        assert (condition | valid) is condition

    def test_returns_self_if_other_is_or_condition(self, valid):
        condition = valid | valid
        condition2 = valid | valid
        assert (condition | condition2) is condition

    def test_else_returns_a_new_condition(self, valid):
        condition = valid | valid
        condition2 = valid & valid
        result = condition | condition2
        assert result is not condition
        assert isinstance(result, OrCondition)


class TestAnd(object):
    def test_returns_an_and_condition(self, valid):
        condition = valid | valid
        result = condition & valid
        assert isinstance(result, AndCondition)
