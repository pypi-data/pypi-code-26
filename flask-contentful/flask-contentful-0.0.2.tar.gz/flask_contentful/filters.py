from flask import Markup
from markdown import markdown


def markdown_filter(text):
    return Markup(markdown(text))
