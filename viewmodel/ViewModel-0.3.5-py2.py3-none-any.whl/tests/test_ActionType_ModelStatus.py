from enum import EnumMeta

import pytest

from viewmodel.viewModel import ActionType
from viewmodel.viewModel import ModelStatus


class TestActionType:
    def test_if_it_inherits_from_OEnum(self):
        assert isinstance(ActionType, EnumMeta)

    def test_attributes(self):
        assert hasattr(ActionType, 'Delete')
        assert hasattr(ActionType, 'Insert')


class TestModelStatus:
    def test_default_constructor(self):
        test = ModelStatus()
        assert test.action is None

    def test_constructor_with_setting_action(self):
        test = ModelStatus(ActionType.Delete)
        assert test.action is ActionType.Delete

    def test_if_constructor_raises_exception_when_gives_wrong_value(self):
        with pytest.raises(ValueError) as e:
            ModelStatus('Must break the code')

        assert str(e.value) == """Expected type of `action`: None or `ActionType`"""
