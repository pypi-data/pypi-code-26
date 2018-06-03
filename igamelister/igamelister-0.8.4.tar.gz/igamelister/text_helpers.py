def repeat(chars: str, count: int) -> str:
    """Return a string of repeated characters.

    :param chars: The characters to repeat.
    :param count: The number of times to repeat.
    :return: The string of repeated characters.
    """
    return chars * count


def truncate(source, max_len: int, el: str = "...", align: str = "<") -> str:
    """Return a truncated string.

    :param source: The string to truncate.
    :param max_len: The total length of the string to be returned.
    :param el: The ellipsis characters to append to the end of the string if it exceeds max_len.
    :param align: The alignment for the string if it does not exceed max_len.
    :return: The truncated string.
    """
    if type(source) is int:
        source = str(source)

    if source is not None and len(source) > 0:
        if len(source) < max_len:
            return source
        elif max_len < len(el) + 1:
            return "{s:{c}{a}{n}}".format(s=source[0], c=".", a=align, n=max_len)
        else:
            return source[:max_len - len(el)] + el if len(source) > max_len else source
    else:
        return ""


def pad(source: str, pad_len: int, align: str) -> str:
    """Return a padded string.

    :param source: The string to be padded.
    :param pad_len: The total length of the string to be returned.
    :param align: The alignment for the string.
    :return: The padded string.
    """
    return "{s:{a}{n}}".format(s=source, a=align, n=pad_len)
