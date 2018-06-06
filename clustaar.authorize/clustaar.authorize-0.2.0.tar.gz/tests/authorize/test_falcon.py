from clustaar.authorize.falcon import authorize
from clustaar.authorize import Ability, Authorizations, Action
from unittest.mock import Mock
import pytest


class AuthorizationsMock(Authorizations):
    def __init__(self, allowed):
        self._allowed = allowed

    def can(self, action, *args, **kwargs):
        return self._allowed


@pytest.fixture
def request():
    return Mock()


@pytest.fixture
def action():
    return Action(name="list_projects")


@pytest.fixture
def callback():
    return Mock()


class TestDecorator(object):
    def test_raises_exception_if_not_authorized(self, request, action, callback):
        request.context.ability = Ability(AuthorizationsMock(False))

        def on_get(handler, req, resp, callback):
            callback()

        with pytest.raises(Exception):
            authorize(action)(on_get)(None, request, None, callback)

        assert callback.call_count == 0

    def test_calls_handler_if_authorized(self, request, action, callback):
        request.context.ability = Ability(AuthorizationsMock(True))

        def on_get(handler, req, resp, callback):
            callback()

        authorize(action)(on_get)(None, request, None, callback)

        callback.assert_called_once_with()
