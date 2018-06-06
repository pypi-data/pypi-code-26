from clustaar.authorize import Authorizations, Action
from clustaar.authorize.rules import Deny, Allow
import pytest


@pytest.fixture
def authorizations(view_project):
    return Authorizations(
        rules={
            view_project: Allow()
        },
        default_rule=Deny()
    )


@pytest.fixture
def view_project():
    return Action(name="view_project")


class TestGenerateError(object):
    def test_returns_an_exception(self, authorizations, view_project):
        exception = authorizations.generate_error(view_project, {})
        assert str(exception) == "Access denied for view_project ({})"


class TestCan(object):
    def test_returns_false_if_default_view_project_is_deny(self, authorizations):
        action = Action(name="other")
        assert not authorizations.can(action, {})

    def test_returns_true_if_default_view_project_is_allow(self, view_project):
        action = Action(name="other")
        authorizations = Authorizations({}, default_rule=Allow())
        assert authorizations.can(action, {})

    def test_returns_rule_result_if_action_rule_is_set(self, authorizations, view_project):
        assert authorizations.can(view_project, {})


class TestExtend(object):
    def test_override_existing_rule(self, authorizations, view_project):
        authorizations.extend({
            view_project: Deny()
        })
        assert not authorizations.can(view_project, {})
