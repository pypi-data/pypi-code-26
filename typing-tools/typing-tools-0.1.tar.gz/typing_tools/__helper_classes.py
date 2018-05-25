from typing import List, Set, Dict
from typing_tools.__common import _getter, _HELPER_CLASSES

def _helper_class_metaclass__generator(argument_id=0):
    def _helper_class_metaclass(future_class_name, future_class_parents, future_class_attributes):
        def __init__(self, _initial_type, *args, __owner__, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)
            self.__args__ = _initial_type
            self.__owner__ = __owner__
        def __getitem__(self, *args, **kwargs):
            value = self.__owner__.__getitem__(*args, **kwargs)
            return _getter(self.__args__[argument_id], value)
        def __setitem__(self, *args, **kwargs):
            return self.__owner__.__setitem__(*args, **kwargs)
        
        future_class_attributes['__init__'] = __init__
        future_class_attributes['__getitem__'] = __getitem__
        future_class_attributes['__setitem__'] = __setitem__

        _class = type(future_class_name, future_class_parents, future_class_attributes)
        _HELPER_CLASSES.append(_class)
        return _class
    return _helper_class_metaclass

class __ListChild(List, metaclass=_helper_class_metaclass__generator()):
    def __iter__(self):
        for value in self.__owner__.__iter__():
            yield _getter(self.__args__[0], value)
    def append(self, *args, **kwargs):
        self.__owner__.append(*args, **kwargs)
class __SetChild(Set, metaclass=_helper_class_metaclass__generator()):
    def __iter__(self):
        for value in self.__owner__.__iter__():
            yield _getter(self.__args__[0], value)
    def set(self, *args, **kwargs):
        self.__owner__.set(*args, **kwargs)
class __DictChild(Dict, metaclass=_helper_class_metaclass__generator(1)):
    def items(self):
        for key, value in self.__owner__.items():
            yield key, _getter(self.__args__[1], value)
    def get(self, *args, **kwargs):
        return _getter(self.__args__[1], super(self.__class__, self).get(*args, **kwargs))

# class __TupleChild(Tuple):
#     def __init__(self, _type, *args, **kwargs):
#         super(self.__class__, self).__init__(*args, **kwargs)
#         self.__arg__ = (_type, )
#     def __getitem__(self, index):
#         value = super(self.__class__, self).__getitem__(index)
#         return _getter(self.__arg__[index], value)
#     def __iter__(self):
#         for index, value in enumerate(super(self.__class__, self).__iter__()):
#             yield _getter(self.__arg__[index], value)
