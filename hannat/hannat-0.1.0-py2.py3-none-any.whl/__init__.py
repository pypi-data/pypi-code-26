# -*- coding: utf-8 -*-
from __future__ import absolute_import

import importlib

__version__ = '0.1.0'


def translit(text, lang="ja"):
    """Transliterate language using google transliterate CGI
        text (str): target string to transliterate
        lang (str, optional): Defaults to "ja"
    
    Returns:
        t: Transliterator for specific language
    """

    cgi = importlib.import_module('hannat.cgi')
    t = cgi.Translit()
    return getattr(t, lang)(text)
