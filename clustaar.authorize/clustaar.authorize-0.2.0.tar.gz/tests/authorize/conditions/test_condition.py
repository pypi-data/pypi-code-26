import pytest
from clustaar.authorize.conditions import TrueCondition, FalseCondition


@pytest.fixture
def invalid():
    return FalseCondition()


@pytest.fixture
def valid():
    return TrueCondition()


class TestAnd(object):
    def test_returns_an_and_condition(self, valid, invalid):
        condition = valid & invalid
        assert not condition({})


class TestOr(object):
    def test_returns_an_and_condition(self, valid, invalid):
        condition = valid | invalid
        assert condition({})
