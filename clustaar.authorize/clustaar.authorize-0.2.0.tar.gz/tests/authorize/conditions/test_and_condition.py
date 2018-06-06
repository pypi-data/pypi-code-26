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
    def test_returns_true_if_all_conditions_are_met(self, valid):
        condition = AndCondition([valid, valid])
        assert condition({})

    def test_returns_false_if_one_condition_is_not_met(self, valid, invalid):
        condition = AndCondition([valid, invalid, valid])
        assert not condition({})


class TestAnd(object):
    def test_returns_self_if_other_is_a_validator(self, valid):
        condition = valid & valid
        assert (condition & valid) is condition

    def test_returns_self_if_other_is_and_condition(self, valid):
        condition = valid & valid
        condition2 = valid & valid
        assert (condition & condition2) is condition

    def test_else_returns_a_new_condition(self, valid):
        condition = valid & valid
        condition2 = valid | valid
        result = condition & condition2
        assert result is not condition
        assert isinstance(result, AndCondition)


class TestOr(object):
    def test_returns_an_or_condition(self, valid):
        condition = valid & valid
        result = condition | valid
        assert isinstance(result, OrCondition)
