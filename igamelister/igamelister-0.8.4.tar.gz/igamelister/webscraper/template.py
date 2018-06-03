import logging
import os
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path

import requests
from lxml import html
from requests import Response

from igamelister.webscraper.interpolation import TemplateInterpolation


class Template:

    logger = logging.getLogger(__name__)

    def __init__(self, file: str, **kwargs):
        self._template = {}
        self._interpolator = TemplateInterpolation(**kwargs)

        if file is not None:
            self._read(file)

    def get(self, key: str, idx: int = None) -> list:
        if key in self._template:
            if idx is not None:
                return self._template[key][idx]
            else:
                return self._template[key]
        else:
            return []

    def get_string(self, key: str, sep: str = '', idx: int = None) -> str:
        if key in self._template:
            return sep.join(self.get(key, idx))
        else:
            return ''

    def get_datetime(self, key: str, fmt, idx: int = None) -> datetime:
        if key in self._template:
            if type(fmt) == str:
                try:
                    return datetime.strptime(self.get_string(key, idx=idx), fmt)
                except ValueError:
                    return datetime.min
            elif type(fmt) == list:
                for x in fmt:
                    try:
                        return datetime.strptime(self.get_string(key, idx=idx), x)
                    except ValueError:
                        pass
        else:
            return datetime.min

    def get_datetime_format(self, key: str, fmt: list, idx: int = None) -> str:
        if key in self._template:
            for x in fmt:
                try:
                    datetime.strptime(self.get_string(key, idx=idx), x)
                    return x
                except ValueError:
                    pass
        else:
            return ""

    def get_list(self, key: str, idx: int = None):
        if key in self._template:
            r = self.get(key, idx)
            if type(r) is list:
                return r
            elif type(r) is str:
                return [r]
        else:
            return []

    def get_int(self, key: str, idx: int = None):
        if key in self._template:
            try:
                return int(self.get_string(key, idx=idx))
            except ValueError:
                return 0
        else:
            return 0

    def _read(self, file: str):
        c = ConfigParser(interpolation=self._interpolator)
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        c.read(Path(os.path.join(curr_dir, "templates", file)))

        if len(c.sections()) > 0:

            url = c['template']['page_url']

            web = self._get_document(url)
            doc = html.fromstring(web.content)

            for cs in c.sections():
                if cs == 'template':
                    continue

                def strip_quotes(s):
                    return s.replace('"', '')

                def decode_string(s):
                    return bytes(s, "utf-8").decode("unicode_escape")

                ignore = [decode_string(x.strip())
                          for x in c.get(cs, 'ignore').split(",")] if c.has_option(cs, 'ignore') else []

                ignore_empty = c.getboolean(cs, 'ignore_empty') if c.has_option(cs, 'ignore_empty') else None

                remove = [strip_quotes(decode_string(x.strip()))
                          for x in c.get(cs, 'remove').split(",")] if c.has_option(cs, 'remove') else []

                replace = [decode_string(x.strip())
                           for x in c.get(cs, 'replace').split(",")] if c.has_option(cs, 'replace') else []

                is_bool = c.getboolean(cs, 'bool') if c.has_option(cs, 'bool') else None

                element_tree = c.getboolean(cs, 'element_tree') if c.has_option(cs, 'element_tree') else None

                join = c.getboolean(cs, 'join') if c.has_option(cs, 'join') else None

                split = strip_quotes(decode_string(c.get(cs, 'split'))) if c.has_option(cs, 'split') else None

                xpath = decode_string(c.get(cs, 'xpath')) if c.has_option(cs, 'xpath') else None

                css_selector = decode_string(c.get(cs, 'css_selector')) if c.has_option(cs, 'css_selector') else None

                self._template[cs] = self._get_value(doc, xpath, css_selector, ignore, remove, replace,
                                                     split, is_bool, ignore_empty, element_tree)

                self._template[cs] = ''.join(self._template[cs]) if join else self._template[cs]

    @staticmethod
    def _get_document(page_url: str) -> Response:
        if page_url is not None:
            try:
                document = requests.get(page_url)
            except requests.ConnectionError:
                Template.logger.error(f"Unable to establish connection to '{page_url}'.")
                raise
            except requests.Timeout:
                Template.logger.error(f"Connection timed out requesting '{page_url}'.")
                raise
            except requests.TooManyRedirects:
                Template.logger.error(f"Too many redirects while requesting '{page_url}'.")
                raise

            if document.status_code != 200:
                Template.logger.error(f"Status code returned {document.status_code} for '{page_url}'.")
                document.raise_for_status()
            else:
                return document

    @staticmethod
    def _get_value(doc, xpath, css_selector, ignore, remove, replace, split, is_bool, ignore_empty, tree):
        def set_bool(s):
            true = ['yes', 'on', 'true']
            false = ['no', 'off', 'false']
            if s.lower() in true:
                return True
            elif s.lower() in false:
                return False
            else:
                return

        if xpath is not None:
            x = doc.xpath(xpath)
        elif css_selector is not None:
            x = doc.cssselect(css_selector)
        else:
            return

        if tree:
            return x

        if type(x) == float:
            return [str(int(x))]

        r = []
        for y in x:
            try:
                v = str(y.text_content())
            except AttributeError:
                v = str(y)

            if ignore_empty:
                if v.strip() == "":
                    continue
            if v in ignore:
                continue

            for rv in remove:
                v = v.replace(rv, "")

            for nv in replace:
                nv = nv.split('|')
                v = v.replace(nv[0], nv[1]) if nv[0] in v else v

            v = v.strip()
            v = set_bool(v) if is_bool else v
            v = v.split(split) if split is not None else v

            r.append(v)
        return r
