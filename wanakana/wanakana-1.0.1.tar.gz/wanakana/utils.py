from wanakana.constants import PROLONGED_SOUND_MARK


def is_char_in_range(char: str, start: int, end: int) -> bool:
    if not char:
        return False

    code: int = ord(char)
    return start <= code <= end


def is_char_long_dash(char: str = ""):
    if not char:
        return False

    code: int = ord(char)
    return code == PROLONGED_SOUND_MARK
