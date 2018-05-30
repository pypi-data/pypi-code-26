# -*- coding: utf-8 -*-

"""
Created on 2016-07-01
:author: Oshane Bailey (b4.oshany@gmail.com)
"""

from __future__ import absolute_import

from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource


library = Library("kotti_alert", "static")

css = Resource(
    library,
    "styles.css",
    minified="styles.min.css")
cookie = Resource(
    library,
    "js.cookie.js")
js = Resource(
    library,
    "scripts.js",
    depends=[cookie],
    minified="scripts.min.js")

css_and_js = Group([css, js])
