# -*- coding: utf-8 -*-

from jinja2.ext import Extension
from stringcase import (
    alphanumcase, camelcase, capitalcase, constcase, snakecase, lowercase,
    pascalcase, pathcase, sentencecase, spinalcase, titlecase, trimcase,
    uppercase,
)


class StringCaseExtension(Extension):
    def __init__(self, environment):
        super(StringCaseExtension, self).__init__(environment)
        environment.filters['camelcase'] = camelcase
        environment.filters['capitalcase'] = capitalcase
        environment.filters['constcase'] = constcase
        environment.filters['lowercase'] = lowercase
        environment.filters['pascalcase'] = pascalcase
        environment.filters['pathcase'] = pathcase
        environment.filters['sentencecase'] = sentencecase
        environment.filters['snakecase'] = snakecase
        environment.filters['spinalcase'] = spinalcase
        environment.filters['titlecase'] = titlecase
        environment.filters['trimcase'] = trimcase
        environment.filters['uppercase'] = uppercase
        environment.filters['alphanumcase'] = alphanumcase
