from wanakana.hiragana import is_char_hiragana
from wanakana.katakana import is_char_katakana


def is_kana(text: str) -> bool:
    if not text:
        return False

    return all(is_char_kana(char) for char in text)


def any_kana(text: str) -> bool:
    if not text:
        return False

    return any(is_char_kana(char) for char in text)


def is_char_kana(char: str) -> bool:
    if not char:
        return False

    return is_char_hiragana(char) or is_char_katakana(char)
