
import itertools
from random import randrange

UPPERCASE = [chr(i) for i in range(65, 91)]  # A to Z
LOWERCASE = [chr(i) for i in range(97, 123)]  # a to z
NUMBERS = [chr(i) for i in range(48, 58)]  # 0 to 9
SYMBOLS = [chr(i) for i in range(33, 48)]  # ! to /
DEFAULT_CHARSETS = [UPPERCASE, LOWERCASE, NUMBERS]
DEFAULT_LENGTH = 8


def randpwd(length=DEFAULT_LENGTH, charsets=DEFAULT_CHARSETS, include_all_charsets=True):
    l = []
    if include_all_charsets == True:
        # get one character from each charset
        assert length >= len(charsets)
        for i in range(len(charsets)):
            charset = charsets[i]
            l.append(charset[randrange(len(charset))])

    # get the rest of the characters from the whole charset
    charset = list(itertools.chain(*charsets))
    l += [charset[randrange(len(charset))] for i in range(len(l), length)]

    # mix all the characters for additional randomness
    for i in range(len(l)):
        pos = randrange(len(l))
        l[i], l[pos] = l[pos], l[i]

    return "".join(l)
