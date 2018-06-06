import pytest
from clustaar.authorize.conditions import TrueCondition


@pytest.fixture
def condition():
    return TrueCondition()


class TestCall(object):
    def test_returns_true(self, condition):
        assert condition({})
