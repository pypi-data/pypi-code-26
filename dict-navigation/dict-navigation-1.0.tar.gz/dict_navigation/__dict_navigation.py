from functools import reduce
from typing import Dict, Any, Type

__DEFAULT_OBJECT = object()

def __get_element_in_dict_object(dict_object: Dict[str, Any], key_path: str, skip_value_field: bool):
    _keys = key_path.split('/')
    return reduce(lambda d, key: d['value'][key] if (skip_value_field and 'value' in d and key in d['value']) else d[key], _keys, dict_object)

def __set_element_in_dict_object(dict_object: Dict[str, Any], key_path: str, value: Any, skip_value_field: bool):
    _keys = key_path.split('/')
    _parent = __get_element_in_dict_object(dict_object, '/'.join(_keys[:-1]), skip_value_field)
    if (skip_value_field and _keys[-2] != 'value' and _keys[-1] != 'value' and 'value' in _parent):
        _parent = _parent['value']
    _parent[_keys[-1]] = value

def get_element_in_dict_object(dict_object: Dict[str, Any], key_path: str, default_value=__DEFAULT_OBJECT, *, skip_value_field: bool = False) -> Any:
    try:
        _value = __get_element_in_dict_object(dict_object, key_path, skip_value_field)
    except KeyError:
        if (default_value is not __DEFAULT_OBJECT):
            return default_value
        else:
            raise KeyError("No such path: {key_path}".format(key_path=key_path))
    else:
        return _value

def has_element_in_dict_object(dict_object: Dict[str, Any], key_path: str, *, skip_value_field: bool = False) -> bool:
    try:
        __get_element_in_dict_object(dict_object, key_path, skip_value_field)
    except KeyError:
        return False
    else:
        return True

def set_element_in_dict_object(dict_object: Dict[str, Any], key_path: str, value, *, recursive=False, new_dict_constructor:Type[Dict]=dict, skip_value_field: bool = False) -> None:
    try:
        __set_element_in_dict_object(dict_object, key_path, value, skip_value_field)
    except KeyError:
        if (recursive):
            _keys = key_path.split('/')
            set_element_in_dict_object(dict_object=dict_object, key_path='/'.join(_keys[:-1]), value=new_dict_constructor(), recursive=True, new_dict_constructor=new_dict_constructor, skip_value_field=skip_value_field)
            __set_element_in_dict_object(dict_object, key_path, value, skip_value_field)
        else:
            raise KeyError("No such path: {key_path}".format(key_path=key_path))
