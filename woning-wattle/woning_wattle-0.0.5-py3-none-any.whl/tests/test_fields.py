import pytest

from wattle import Integer, Boolean, Float, String, load_schema, Choice
from wattle.exceptions import InvalidValueError


@pytest.mark.parametrize('field, value, expected_value, raises', [
    (Integer(), 10, 10, False),
    (Integer(), '10', 10, False),
    (Integer(), 'false', None, True),
    (Float(), 3.14, 3.14, False),
    (Float(), '3.14', 3.14, False),
    (Float(), 'pi', None, True),
    (String(), 10, '10', False),
    (String(), 100.11, '100.11', False),
    (String(), 'test', 'test', False),
    (String(), False, 'False', False),
    (Boolean(), 0, False, False),
    (Boolean(), 1, True, False),
    (Boolean(), 'test', True, False),
    (Boolean(), '', False, False),
    (Boolean(), False, False, False),
    (Boolean(), True, True, False),
    (Boolean(), None, False, False),
])
def test_integer_field(field, value, expected_value, raises):
    class Schema:
        myval = field

    schema = load_schema(Schema)
    if raises:
        with pytest.raises(InvalidValueError):
            _ = schema.read_dict({'myval': value})
    else:
        obj = schema.read_dict({'myval': value})
        assert obj.myval == expected_value


def test_choice_field():
    class Schema:
        myval = Choice(['a', 'b', 'c'])

    schema = load_schema(Schema)
    obj = schema.read_dict({'myval': 'a'})
    assert obj.myval == 'a'
    with pytest.raises(InvalidValueError):
        _ = schema.read_dict({'myval': 'd'})
    obj = schema.read_dict({})
    assert obj.myval == 'a'
