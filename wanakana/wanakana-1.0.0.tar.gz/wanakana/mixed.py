from wanakana.hiragana import is_hiragana
from wanakana.kanji import is_kanji
from wanakana.katakana import is_katakana
from wanakana.romaji import is_romaji


def is_mixed(text: str, pass_kanji=True) -> bool:
    has_kanji = False

    if not pass_kanji:
        has_kanji = any(is_kanji(char) for char in text)

    is_hiragana_or_katakana = any(is_hiragana(char) for char in text) or any(
        is_katakana(char) for char in text
    )

    return (
        is_hiragana_or_katakana
        and any(is_romaji(char) for char in text)
        and not has_kanji
    )
