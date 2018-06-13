from collections import abc
from keyword import iskeyword


class FrozenJSON:
    def __new__(cls, arg):
        if isinstance(arg, abc.Mapping):
            obj = super().__new__(cls)
            obj.json = arg
            return obj
        elif isinstance(arg, abc.MutableSequence):
            return [cls(item) for item in arg]
        else:
            return arg

    def __init__(self, mapping):
        self.__data = {}
        for key, value in mapping.items():
            if iskeyword(key):
                key += '_'
            if isinstance(key, str):
                if '-' in key:
                    key = key.replace('-', '_')
                if key[0] in [str(i) for i in range(10)]:
                    key = '_' + key
            else:
                key = '_' + str(type(key)) + '_' + str(key)
            self.__data[key] = value

    def __getattr__(self, name):
        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            return FrozenJSON(self.__data[name]) if self.__data.get(name) is not None else None
