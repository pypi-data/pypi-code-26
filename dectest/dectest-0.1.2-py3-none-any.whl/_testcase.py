"""
Custom test case class to replace unittest's TestCase class.
"""

import unittest
from typing import cast, Any, List, Type, Dict, Tuple, TypeVar
from unittest.mock import patch

from ._types import TestMethod

_C = TypeVar("_C")


def _is_test_method(method: Any) -> bool:
    if not callable(method):
        return False
    return hasattr(method, "_dectest_test")


class _TestCaseMeta(type):
    def __new__(mcs: Type[_C], name: str, bases: Tuple[type, ...],
                dct: Dict[str, Any]) -> _C:
        test_methods = [(attr_name, method)
                        for attr_name, method in dct.items()
                        if _is_test_method(method)]
        for attr_name, method in test_methods:
            del dct[attr_name]
            dct["test__" + attr_name] = method
        return cast(_C, super().__new__(mcs, name, bases, dct))


class TestCase(unittest.TestCase, metaclass=_TestCaseMeta):
    """Drop-in replacement for unittest's TestCase class.

    This class supports the @before and @after decorators.

    If you use setUp() or tearDown(), you need to call the super
    implementations from those methods for @before and @after to work.
    """

    def setUp(self) -> None:
        self._dectest_patches = []  # type: List[Any]
        methods = reversed(self._get_decorated_methods("_dectest_before"))
        for method in methods:
            method(self)

    def tearDown(self) -> None:
        for method in self._get_decorated_methods("_dectest_after"):
            method(self)
        for p in self._dectest_patches:
            p.stop()

    def _get_decorated_methods(self, attr_name: str) -> List[TestMethod]:
        """Return all methods of this class that have a certain attribute.

        Methods are returned in subclass-first order.
        """

        def get_methods_in_class(class_: type) -> List[TestMethod]:
            return [
                value for name, value in vars(class_).items()
                if callable(value) and hasattr(value, attr_name)
            ]

        classes = type(self).mro()
        methods = [get_methods_in_class(c) for c in classes]
        return [m for m_list in methods for m in m_list]

    def patch(self, target: Any, *args: Any, **kwargs: Any) -> Any:
        """Convenience wrapper for unittest.mock.patch().

        Return the mock object. The patch will be cleaned up during test
        teardown.
        """
        p = patch(target, *args, **kwargs)
        self._dectest_patches.append(p)
        return p.start()
