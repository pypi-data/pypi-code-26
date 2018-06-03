# -*- coding: utf-8 -*-

'''
http://www.google.com/intl/ja/ime/cgiapi.html
>>>from hannat.cgi import Transliterator
>>>api = Transliterator()
>>>result = api.ja('こんにちは')
>>>print result[0][1][1]
今日は
'''

import re
import json
import requests


class Translit(object):
    def __init__(self):
        """Transliterate language using google transliterate CGI"""
        self.lang = 'ja-Hira|ja'
        self.uri = 'http://www.google.com/transliterate?'

    def ja(self, text):
        """Japanese transliterator
        
        Args:
            text (str): target text
        
        Returns:
            candidates: list of transliterate candidates
        """

        params = {
            'langpair' : self.lang,
            'text' : text
        }
        response = requests.get(self.uri, params=params).text
        candidates = json.loads(response)

        return candidates