from clustaar.authorize.rules import Allow
import pytest


@pytest.fixture
def rule():
    return Allow()


class TestCall(object):
    def test_returns_true(self, rule):
        assert rule({})
