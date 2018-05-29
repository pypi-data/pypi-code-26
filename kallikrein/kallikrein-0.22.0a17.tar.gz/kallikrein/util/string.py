from typing import Any

from amino.string.hues import huestr

from amino import __, Lists
from amino.util.string import camelcase


def green(msg: Any) -> str:
    return huestr(str(msg)).green.colorized


def red(msg: Any) -> str:
    return huestr(str(msg)).red.colorized


def yellow(msg: Any) -> str:
    return huestr(str(msg)).yellow.colorized


def blue(msg: Any) -> str:
    return huestr(str(msg)).blue.colorized


def magenta(msg: Any) -> str:
    return huestr(str(msg)).magenta.colorized

indent = __.map(' {}'.format)

green_check = green('✓')

red_cross = red('✗')

yellow_clock = yellow('⌚')

green_plus = green('+')

red_minus = red('-')

spec_sign = '⛤'


def spec_headline(mod: str, cls: str) -> str:
    path = mod if Lists.split(mod, '.').last.map(camelcase).contains(cls) else f'{mod}.{cls}'
    return magenta(f'{spec_sign} {path}')


__all__ = ('indent', 'green_check', 'red_cross', 'green', 'red', 'yellow_clock', 'green_plus', 'red_minus', 'blue',
           'magenta', 'spec_sign', 'spec_headline')
