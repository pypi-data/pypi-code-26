__version__ = '0.0.3'
__author__ = [
    'qorzj <inull@qq.com>',
]

__license__ = "MIT"

from . import dome as _dome
from . import utils as _utils

from .dome import Node, Html, Head, Body, Div, Meta, Title, Script, Link, CssLink, Style, A, Em
from .dome import P, H1, H2, H3, H4, H5, Label, Span
from .utils import escape
