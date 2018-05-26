import hues

_default = hues.huestr('{}').white.colorized
_accent = hues.huestr('{}').green.colorized
_accent2 = hues.huestr('{}').yellow.colorized
_not_ok = hues.huestr('{}').red.colorized
_muted = hues.huestr('{}').black.colorized


def base(content):
    return '{}'.format(
        _default.format(content)
    )


def base_accent(content):
    return '{}'.format(
        _accent.format(content)
    )


def base_accent2(content):
    return '{}'.format(
        _accent2.format(content)
    )


def base_not_ok(content):
    return '{}'.format(
        _not_ok.format(content)
    )


def notice_error(content):
    return (
        newline(2) +
        '{}'.format(
            _not_ok.format(content)
        ) +
        newline(3)
    )


def newline(number=1):
    new_lines = ''
    for _ in range(number-1):
        new_lines += '\n'
    return new_lines
