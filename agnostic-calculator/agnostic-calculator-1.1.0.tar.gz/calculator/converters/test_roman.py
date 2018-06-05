import calculator.converters.roman as roman
import pytest

ROMAN_TO_INT = [
    ('I', 1),
    ('II', 2),
    ('IV', 4), # Special case: 1 before 5
    ('V', 5),
    ('VI', 6),
    ('IX', 9), # Special case: 1 before 10
    ('X', 10),
    ('XI', 11),
    ('XX', 20),
    ('XL', 40), # Special case: 10 before 50
    ('L', 50),
    ('XC', 90), # Special case: 10 before 100
    ('C', 100),
    ('CD', 400), # Special case: 100 before 500
    ('D', 500),
    ('CM', 900), # Special case: 100 before 1000
    ('M', 1000),
    ('MCM', 1900), # Special case: 100 before 2000
    ('MCMXCIX', 1999), # Y2K
    ('MMXVIII', 2018), # Beyond
]
INT_TO_ROMAN = [(y, x) for (x, y) in ROMAN_TO_INT]

# TODO: add test case(s) to cover bad input
@pytest.mark.parametrize('test_input,expected', ROMAN_TO_INT)
def test_to_int(test_input, expected):
    """Test to_int() returns an integer given roman numerals."""
    assert roman.to_int(test_input) == expected

@pytest.mark.parametrize('test_input,expected', INT_TO_ROMAN)
def test_from_int(test_input, expected):
    """Test from_int() returns roman numerals given an integer."""
    assert roman.from_int(test_input) == expected

@pytest.mark.parametrize('test_input,expected', [
    ('IV', True),
    ('IIII', False),
])
@pytest.mark.skip(reason="Method not yet implemented")
def test_validate(test_input, expected):
    """Test validate() returns the appropriate boolean."""
    assert roman.validate(test_input) == expected
