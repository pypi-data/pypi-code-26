from clustaar.authorize import Ability, Authorizations, Action
import pytest


@pytest.fixture
def ability(list_action):
    class AuthorizationsMock(Authorizations):
        def can(self, action, *args, **kwargs):
            return action == list_action

    authorizations = AuthorizationsMock(rules={})
    return Ability(authorizations)


@pytest.fixture
def view_action():
    return Action(name="view_project")


@pytest.fixture
def list_action():
    return Action(name="list_projects")


class TestAuthorize(object):
    def test_raises_exception_if_not_authorized(self, ability, view_action):
        with pytest.raises(Exception):
            ability.authorize(view_action, project_id=1)

    def test_does_nothing_if_allowed(self, ability, list_action):
        ability.authorize(list_action)
