from typing_tools.__common import _getter

class AssignmentSupportable:
    def __getattribute__(self, key: str):
        value = super().__getattribute__(key)
        if (key == '__annotations__'):
            return value
        if (hasattr(self, '__annotations__') and key in self.__annotations__):
            return _getter(self.__annotations__[key], value)
        return value
