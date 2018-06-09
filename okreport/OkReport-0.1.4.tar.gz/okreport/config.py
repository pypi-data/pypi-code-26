# !/usr/bin/python -u

"""
Copyright (C) 2018 LingoChamp Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from ConfigParser import ConfigParser


class Config:
    configParser = None

    def __init__(self, path=""):
        config_parser = ConfigParser()
        config_parser.read(path)
        self.configParser = config_parser

    def mail_domain_name(self):
        return self.configParser.get('MAILGUN', 'DomainName')

    def mail_api_key(self):
        return self.configParser.get('MAILGUN', 'ApiKey')

    def mail_from(self):
        return self.configParser.get('MAILGUN', 'From')

    def mail_to(self):
        value = self.configParser.get('MAILGUN', 'To')
        if value is None:
            return list()
        return value.split(',')

    def mail_cc(self):
        value = self.configParser.get('MAILGUN', 'Cc')
        if value is None:
            return list()
        return value.split(',')

    def mail_subject(self):
        return self.configParser.get('MAILGUN', 'Subject')

    def content_url(self):
        if not self.configParser.has_option('CONTENT', 'DetailUrl'):
            return None
        return self.configParser.get('CONTENT', 'DetailUrl')

    def content_qark_url(self):
        if not self.configParser.has_option('CONTENT', 'QarkReportUrl'):
            return None
        return self.configParser.get('CONTENT', 'QarkReportUrl')
