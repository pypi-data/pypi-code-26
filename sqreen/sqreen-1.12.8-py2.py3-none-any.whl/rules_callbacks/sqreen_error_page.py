# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Base custom error page
"""
from os.path import dirname, join

from ..exceptions import ActionBlock, ActionRedirect, AttackBlocked
from ..rules import RuleCallback
from ..runtime_storage import runtime


class BaseSqreenErrorPage(RuleCallback):

    def __init__(self, *args, **kwargs):
        super(BaseSqreenErrorPage, self).__init__(*args, **kwargs)
        with open(join(dirname(__file__), 'sqreen_error_page.html')) as f:
            self.content = f.read()

        rule_data = self.data["values"][0]
        self.rule_type = rule_data["type"]

        if self.rule_type == 'custom_error_page':
            self.status_code = int(rule_data['status_code'])
            runtime.attack_http_code = self.status_code
        elif self.rule_type == 'redirection':
            self.redirection_url = rule_data['redirection_url']
        else:
            raise ValueError("Invalid rule_type %s" % self.rule_type)

    def pre(self, original, *args, **kwargs):
        exception = self._get_exception(*args, **kwargs)

        if not exception:
            return

        elif isinstance(exception, (ActionBlock, AttackBlocked)):
            if self.rule_type == 'custom_error_page':
                response = self._get_response(exception, self.content, self.status_code)
            elif self.rule_type == 'redirection':
                headers = {'Location': self.redirection_url}
                response = self._get_response(exception, "", 303, headers)

        elif isinstance(exception, ActionRedirect):
            headers = {'Location': exception.target_url}
            response = self._get_response(exception, '', 303, headers)

        else:
            raise RuntimeError("invalid exception type {!r}".format(
                exception.__class__.__name__))

        return {"status": "override", "new_return_value": response}
