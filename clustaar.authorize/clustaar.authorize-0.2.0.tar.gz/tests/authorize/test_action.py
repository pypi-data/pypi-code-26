from clustaar.authorize import Action
import pytest


@pytest.fixture
def action():
    return Action(name="create_project")


class TestConstructor(object):
    def test_set_attributes(self, action):
        assert action.name == "create_project"
