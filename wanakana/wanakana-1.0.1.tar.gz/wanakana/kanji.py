from wanakana.constants import KANJI_START, KANJI_END
from wanakana.utils import is_char_in_range


def is_kanji(text: str) -> bool:
    if not text:
        return False

    return all(is_char_kanji(char) for char in text)


def any_kanji(text: str) -> bool:
    if not text:
        return False

    return any(is_char_kanji(char) for char in text)


def is_char_kanji(char: str) -> bool:
    if not char:
        return False

    return is_char_in_range(char, KANJI_START, KANJI_END)
