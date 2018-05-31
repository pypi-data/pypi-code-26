import os
import ast
from functools import wraps
from contextlib import contextmanager

from typing import Callable


def doc_parametrize(**parameters) -> Callable:
    """
    Decorator for allowing parameters to be passed into docstring

    :param parameters: key value pair that corresponds to the params in docstring
    """
    def decorator_(callable_):
        new_doc = callable_.__doc__.format(**parameters)
        callable_.__doc__ = new_doc

        @wraps(callable_)
        def wrapper(*args, **kwargs):
            return callable_(*args, **kwargs)

        return wrapper

    return decorator_


@contextmanager
def cd(dir_path: str):
    """
    Context manager for cd, change back to original directory when done
    """
    cwd = os.getcwd()
    try:
        os.chdir(os.path.expanduser(dir_path))
        yield
    finally:
        os.chdir(cwd)


def strip_blank_recursive(nested_list: list, evaluate: bool=False):
    """
    Strip blank space or newline characters recursively for a nested list

    *This updates the original list passed in*

    """
    if not isinstance(nested_list, list):
        raise ValueError(f"iterable passed must be type of list. not '{type(nested_list).__name__}'")

    for i, v in enumerate(nested_list):
        if isinstance(v, list):
            strip_blank_recursive(v, evaluate)
        elif isinstance(v, str):
            if not evaluate:
                val_ = v.strip()
            else:
                val_ = str_eval(v)

            nested_list[i] = val_


def str_eval(parse_str: str):
    """
    Evaluate string, return the respective object if evaluation is successful,
    """
    try:
        val = ast.literal_eval(parse_str.strip())
    except (ValueError, SyntaxError):  # SyntaxError raised when passing in "{asctime}::{message}"
        val = parse_str.strip()

    return val