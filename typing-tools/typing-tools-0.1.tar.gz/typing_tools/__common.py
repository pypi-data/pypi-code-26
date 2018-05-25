from typing import List, Type, Iterable

_DEFAULT_OBJECT = object()
_HELPER_CLASSES: List[Type[Iterable]] = list()
_PUBLIC_CLASSES: List[Type[Iterable]] = list()

def _getter(key_type, value):
    for _public_class in _PUBLIC_CLASSES:
        _parent_class = _public_class.__bases__[0]
        if (issubclass(key_type, _public_class) and isinstance(value, _parent_class)):
            debug_msg(f"Creating object of {key_type}")
            return key_type(value, __owner__=value)
            # return key_type(value)

    for _helper_class in _HELPER_CLASSES:
        _parent_class = _helper_class.__bases__[0]
        if (issubclass(key_type, _parent_class) and isinstance(value, _parent_class) and hasattr(key_type, '__args__')):
            debug_msg(f"Creating object of {_helper_class}")
            return _helper_class(key_type.__args__, value, __owner__=value)
    
    return value

def _nop(*args, **kwargs):
    pass

# debug_msg = print
debug_msg = _nop
