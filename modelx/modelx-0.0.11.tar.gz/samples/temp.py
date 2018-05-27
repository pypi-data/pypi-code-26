
import collections

class StrListSubscriptionMixin:

    def __getitem__(self, key):

        if isinstance(key, str):
            return super().__getitem__(key)

        elif isinstance(key, collections.Sequence):
            newmap = type(self)()
            for name in key:
                if not isinstance(name, str):
                    raise KeyError
                else:
                    newmap[name] = self[name]

            return newmap

        else:
            raise KeyError


class CustomDict(StrListSubscriptionMixin, dict):
    pass

d = CustomDict()

d['foo'] = 1
d['bar'] = 2
d['baz'] = 3

class TestSubscr:
    def __getitem__(self, item):
        return item