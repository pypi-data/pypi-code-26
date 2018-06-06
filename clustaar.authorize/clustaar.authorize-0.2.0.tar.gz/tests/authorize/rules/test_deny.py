from clustaar.authorize.rules import Deny
import pytest


@pytest.fixture
def rule():
    return Deny()


class TestCall(object):
    def test_returns_false(self, rule):
        assert not rule({})
