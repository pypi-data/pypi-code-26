ROMAN_NUMERALS = {
    'M': 1000,
    'D': 500,
    'C': 100,
    'L': 50,
    'X': 10,
    'V': 5,
    'I': 1
}

def to_int(string):
    """Produce the integer equivalent of a number represented in Roman numerals."""
    assert isinstance(string, str)
    value = 0
    numerals = [ROMAN_NUMERALS[x] for x in list(string.upper())]
    for i, numeral in enumerate(numerals):
        if i+1 == len(numerals): # The last number
            value += numeral
        elif numeral < numerals[i+1]: # A number smaller than the num to its right
            value -= numeral
        else:
            value += numeral

    return value

def from_int(integer):
    """Produce a string representing the input integer in Roman numerals."""
    string = ""
    numbers = {ROMAN_NUMERALS[x] : x for x in ROMAN_NUMERALS}
    remainder = integer
    for number, roman in numbers.items():
        if remainder == 0:
            break
        if remainder >= number:
            char_count = int(remainder/number)
            string += roman * char_count
            remainder = remainder % number
        # The fun cases:
        if number in [1000, 500] and remainder >= number - 100:
            string += "C" + roman
            remainder -= (number - 100)
        elif number in [100, 50] and remainder >= number - 10:
            string += "X" + roman
            remainder -= number - 10
        elif number in [10, 5] and remainder >= number -1:
            string += "I" + roman
            remainder -= number - 1

    return string

def validate(string):
    """Verify input string correctly represents a number in Roman numerals.
    For example, IV is valid while IIII is not, NM is not.
    """
    # TODO: I'm not implementing this now, but it's worth doing
    pass
