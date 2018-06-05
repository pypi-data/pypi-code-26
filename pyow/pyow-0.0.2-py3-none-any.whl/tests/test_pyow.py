import pytest

from pyow import pyow
from pyow.exceptions import ArgumentError


def test_pyow_is_valid():
    assert pyow.is_valid(1, pyow.number)
    assert pyow.is_valid('str', pyow.string)
    assert pyow.is_valid('str', pyow.string.length(3))
    assert not pyow.is_valid('str', pyow.string.min_length(5))


def test_create_reusable_validator():
    string_check = pyow.create(pyow.string.min_length(6))

    string_check('foobar')
    string_check('foobars')
    string_check('foobarsy')
    with pytest.raises(ArgumentError):
        string_check('foo')


def test_nix_operator():
    pyow(1, pyow.number.nix.infinite)
    pyow(1, pyow.number.nix.infinite.greater_than(5))
    pyow('monkey!', pyow.string.nix.alphanumeric)

    with pytest.raises(ArgumentError, match='NOT Expected string to be empty, got ``'):
        pyow('', pyow.string.nix.empty)
