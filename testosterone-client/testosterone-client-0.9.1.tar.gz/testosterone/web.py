#!/usr/bin/python
# -*- coding: UTF-8 -*-
r"""
@author: Martin Klapproth <martin.klapproth@googlemail.com>
"""

import logging
from collections import defaultdict
from copy import deepcopy
from http.cookiejar import CookieJar
from json import JSONDecodeError
from pprint import pprint
from urllib.parse import urlparse, parse_qs

import requests

from testosterone.runner import TestosteroneRunner

logger = logging.getLogger(__name__)

WEB_REGISTRY = {}


class ResponseWrapper(object):
    def __init__(self, response):
        """
        @type response: requests.Response
        """
        self.response = response  # type: requests.Response

    def __str__(self):
        return self.response.__str__()

    def json(self):
        """

        @rtype: dict
        """
        return self.response.json()

    def print(self):
        if self.response.headers.get('Content-Type', "").startswith("application/json"):
            pprint(self.response.json())
            return self

        print(self.response.text)
        return self

    def debug(self):
        request = self.response.request

        print("%s %s" % (request.method, request.url))

        headers = [(k, v) for k, v in request.headers.items()]
        headers.sort()

        for k, v in headers:
            print("%s: %s" % (k, v))

        if request.body:
            print()
            if len(request.body) > 200:
                print(request.body[:200])
                print("... request body truncated ...")
            else:
                print(request.body)

        print()

        print("%s %s" % (self.response.status_code, self.response.reason))

        headers = [(k, v) for k, v in self.response.headers.items()]
        headers.sort()

        for k, v in headers:
            print("%s: %s" % (k, v))

        return self

    def profile(self):
        pass

    @property
    def status_code(self):
        """
        @rtype: int
        @return:
        """
        return self.response.status_code

    def assert_contains(self, text):
        """
        @rtype:  ResponseWrapper
        """
        assert text in self.response.text, "Text '%s' could not be found in response, response: \n%s" % (text, self.response.text)
        return self

    def assert_not_contains(self, text):
        """
        @rtype:  ResponseWrapper
        """
        assert text not in self.response.text, "Text '%s' could be found in response, response: \n%s" % (text, self.response.text)
        return self

    def assert_status(self, status_code):
        """
        @rtype:  ResponseWrapper
        """
        assert self.status_code == status_code, "Response status %s does not match expected %s" % (self.status_code, status_code)
        return self

    def assert_json(self):
        """
        @rtype:  ResponseWrapper
        """
        try:
            self.response.json()
        except JSONDecodeError as e:
            raise JSONDecodeError(str(e) + "\n" + self.response.text, e.doc, e.pos)
        return self

    def assert_success(self):
        """
        @rtype:  ResponseWrapper
        """
        return self.assert_status(200)

    def assert_html(self):
        """
        @rtype:  ResponseWrapper
        """
        if not "html" in self.response.headers.get("Content-Type"):
            raise AssertionError("Content-Type is not html")
        if not self.response.text.startswith("<"):
            raise AssertionError("Body does not start with '<'")
        return self


class WebWrapper():
    def __init__(self, name, prefix="", **kwargs):
        self.prefix = prefix
        self.cookies = defaultdict(dict)
        self.headers = {}
        self.session = requests.session()

    def set_headers(self, headers):
        self.headers = headers
        # , headers={"X-Requested-With": "XMLHttpRequest"}

    def build_url(self, uri):
        if uri.startswith("http://") or uri.startswith("https://"):
            return uri

        prefix = self.prefix
        prefix = prefix.rstrip("/")
        uri = uri.lstrip("/")
        return prefix + "/" + uri

    def update_cookies(self, response):
        """
        @type response: requests.Response
        @return:
        """
        netloc = urlparse(response.url).netloc

        cookie_line = response.headers.get("Set-Cookie")
        if not cookie_line:
            return

        cookie_line = cookie_line.replace("Sun, ", "").replace("Mon, ", "").replace("Tue, ", "")\
            .replace("Wed, ", "").replace("Thu, ", "").replace("Fri, ", "").replace("Sat, ", "")

        cookie_lines = cookie_line.split(",")
        for line in cookie_lines:
            line = line.strip()
            key, value = line.split(";")[0].split("=")
            self.cookies[netloc][key] = value

    def get_cookies(self, url):
        netloc = urlparse(url).netloc
        cookie_dict = self.cookies[netloc]
        if not cookie_dict:
            return

        return cookie_dict

    def get_headers(self, headers=None):
        new_headers = deepcopy(self.headers)
        if headers:
            new_headers.update(headers)

        cookie = self.get_cookies(self.current_url)
        if cookie:
            new_headers["Cookie"] = cookie

        return new_headers

    def get(self, uri="", **kwargs):
        """

        @param uri:
        @param kwargs:
        @return:
        @rtype: ResponseWrapper
        """
        self.current_url = url = self.build_url(uri)

        logger.debug("GET %s" % url)
        
        headers = deepcopy(self.headers)
        headers.update(kwargs.get("headers", {}))
        kwargs["headers"] = headers

        self.session.cookies = CookieJar()
        response = self.session.get(url, cookies=self.get_cookies(url), **kwargs)

        self.update_cookies(response)
        return ResponseWrapper(response)

    def parse_form_data(self, form_data):
        data = {}

        if type(form_data) == dict:
            return form_data

        if not "\n" in form_data:
            return {k: v[0] for k, v in parse_qs(form_data).items()}

        for line in form_data.strip().splitlines():
            key, value = line.split(":")
            data[key.strip()] = value.strip()

        return data

    def post(self, uri, form_data=None, **kwargs):
        """
        @param uri:
        @param form_data:
        @return:
        """
        data = None

        if form_data:
            data = self.parse_form_data(form_data)

        url = self.build_url(uri)

        headers = deepcopy(self.headers)
        headers.update(kwargs.get("headers", {}))
        kwargs["headers"] = headers

        self.session.cookies = CookieJar()
        response = self.session.post(url, data=data, cookies=self.get_cookies(url), **kwargs)

        if response.history:
            response = response.history[0]

        self.update_cookies(response)
        return ResponseWrapper(response)

    def shutdown(self):
        pass

def Web(name):
    """
    @type name: str
    @rtype: WebWrapper
    """
    if name in WEB_REGISTRY:
        return WEB_REGISTRY[name]

    try:
        web_config = TestosteroneRunner.get_instance().config["web"][name]
    except KeyError:
        print("Web '%s' is not configured" % name)
        exit(3)
        return

    web = WebWrapper(name, **web_config)

    WEB_REGISTRY[name] = web
    return web
