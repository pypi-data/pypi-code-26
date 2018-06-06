from typing import TypeVar

from ._types import TestMethod

_F = TypeVar("_F", bound=TestMethod)


def test(method: _F) -> _F:
    """Decorator that flags a method as a test method."""
    method._dectest_test = True  # type: ignore
    return method


def before(method: _F) -> _F:
    """Decorator that flags a method as fixture setup.

    Fixture setup methods from base classes are guaranteed to be executed
    before setup methods from derived classes.
    """
    method._dectest_before = True  # type: ignore
    return method


def after(method: _F) -> _F:
    """Decorator that flags a method as fixture teardown.

    Fixture teardown methods from base classes are guaranteed to be executed
    after teardown methods from derived classes.
    """
    method._dectest_after = True  # type: ignore
    return method
