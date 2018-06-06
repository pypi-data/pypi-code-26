from unittest.mock import Mock
from clustaar.authorize.rules import AccessRule
from clustaar.authorize.context import Context
import pytest


@pytest.fixture
def resolver(user):
    def handler(context):
        context["user"] = user

    return handler


@pytest.fixture
def condition():
    return Mock(return_value=False)


@pytest.fixture
def user():
    return Mock()


@pytest.fixture
def rule(resolver, condition):
    return AccessRule(resolvers=(resolver,), condition=condition)


class TestCall(object):
    def test_sends_context_to_condition(self, rule, user, condition):
        context = Context(kwargs={"user_id": 1})
        rule(context)
        context = condition.call_args_list[0][0][0]
        assert context["user"] == user

    def test_returns_value_from_condition(self, rule):
        context = Context()
        assert not rule(context)
