from __future__ import unicode_literals
from future.standard_library import install_aliases
install_aliases()

from tornado.web import RequestHandler, asynchronous
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.escape import json_decode
from base.django_handler_mixin import DjangoHandlerMixin
from urllib.parse import urlencode
from django.conf import settings
from allauth.account.models import EmailAddress

class Proxy(DjangoHandlerMixin, RequestHandler):
    @asynchronous
    def post(self, relative_url):
        self.url = settings.PHPLIST_BASE_URL + '/admin/?page=call&pi=restapi'
        self.relative_url = relative_url
        self.login()

    def login(self):
        post_data = {
            'cmd': 'login',
            'login': settings.PHPLIST_LOGIN,
            'password': settings.PHPLIST_PASSWORD
        }
        if hasattr(settings, 'PHPLIST_SECRET'):
            post_data['secret'] = settings.PHPLIST_SECRET
        http = AsyncHTTPClient()
        http.fetch(
            HTTPRequest(
                self.url,
                'POST',
                None,
                urlencode(post_data)
            ),
            callback=self.process_request
        )

    def process_request(self, response):
        if response.error:
            response.rethrow()
        self.session_cookie = response.headers['Set-Cookie']
        if self.relative_url == 'subscribe_email':
            self.subscribe_email()
        else:
            self.set_status(401)
            self.finish()
            return

    def subscribe_email(self):
        email = self.get_argument('email')
        email_object = EmailAddress.objects.filter(email=email).first()
        if not email_object:
            self.finish()
            return
        post_data = {
            'cmd': 'subscriberAdd',
            'email': email,
            'foreignkey': '',
            'confirmed': 1,
            'htmlemail': 1,
            'disabled': 0
        }
        if hasattr(settings, 'PHPLIST_SECRET'):
            post_data['secret'] = settings.PHPLIST_SECRET
        http = AsyncHTTPClient()
        http.fetch(
            HTTPRequest(
                self.url,
                'POST',
                {'Cookie': self.session_cookie},
                urlencode(post_data)
            ),
            callback=self.add_email_to_list
        )

    def add_email_to_list(self, response):
        if response.error:
            response.rethrow()
        response_json = json_decode(response.body)
        if response_json['status'] == 'error':
            # could not create user with this email
            self.finish()
            return
        subscriber_id = response_json['data']['id']
        post_data = {
            'cmd': 'listSubscriberAdd',
            'list_id': settings.PHPLIST_LIST_ID,
            'subscriber_id': subscriber_id
        }
        if hasattr(settings, 'PHPLIST_SECRET'):
            post_data['secret'] = settings.PHPLIST_SECRET
        http = AsyncHTTPClient()
        http.fetch(
            HTTPRequest(
                self.url,
                'POST',
                {'Cookie': self.session_cookie},
                urlencode(post_data)
            ),
            callback=self.respond_to_client
        )

    def respond_to_client(self, response):
        if response.error:
            response.rethrow()
        self.finish()
