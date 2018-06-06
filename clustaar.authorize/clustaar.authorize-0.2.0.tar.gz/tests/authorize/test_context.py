import pytest
from clustaar.authorize.context import Context


@pytest.fixture
def context():
    return Context(args=(1, 2), kwargs={"user_id": 16})


@pytest.fixture
def sentinel():
    return object()


class TestConstructor(object):
    def test_set_attributes_from_kwargs(self, context):
        assert context.user_id == 16


class TestSetItem(object):
    def test_creates_an_attribute(self, context, sentinel):
        context["user"] = sentinel
        assert context.user is sentinel

    def test_fills_the_dictionnary(self, context, sentinel):
        context["user"] = sentinel
        assert context["user"] is sentinel


class TestSetAttr(object):
    def test_set_attribute(self, context, sentinel):
        context.user = sentinel
        assert context.user is sentinel

    def test_fills_the_dictionnary(self, context, sentinel):
        context.user = sentinel
        assert context["user"] is sentinel


class TestUpdate(object):
    def test_merge_values_from_other_dict(self, context):
        context.update({"id": 1})
        assert context["id"] == 1
        assert context.id == 1
