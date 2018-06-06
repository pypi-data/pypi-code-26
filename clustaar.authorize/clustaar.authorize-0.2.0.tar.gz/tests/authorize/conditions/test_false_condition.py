import pytest
from clustaar.authorize.conditions import FalseCondition


@pytest.fixture
def condition():
    return FalseCondition()


class TestCall(object):
    def test_returns_false(self, condition):
        assert not condition({})
