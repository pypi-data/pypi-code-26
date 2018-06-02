from wanakana.constants import HIRAGANA_START, HIRAGANA_END
from wanakana.utils import is_char_long_dash, is_char_in_range


def is_hiragana(text: str) -> bool:
    if not text:
        return False

    return all(is_char_hiragana(char) for char in text)


def any_hiragana(text: str) -> bool:
    if not text:
        return False

    return any(is_char_hiragana(char) for char in text)


def is_char_hiragana(char: str) -> bool:
    if not char:
        return False

    if is_char_long_dash(char):
        return True

    return is_char_in_range(char, HIRAGANA_START, HIRAGANA_END)
