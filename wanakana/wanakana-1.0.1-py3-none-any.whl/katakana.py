from wanakana.constants import KATAKANA_START, KATAKANA_END
from wanakana.utils import is_char_in_range


def is_katakana(text: str) -> bool:
    if not text:
        return False

    return all(is_char_katakana(char) for char in text)


def any_katakana(text: str) -> bool:
    if not text:
        return False

    return any(is_char_katakana(char) for char in text)


def is_char_katakana(char: str) -> bool:
    if not char:
        return False

    return is_char_in_range(char, KATAKANA_START, KATAKANA_END)
