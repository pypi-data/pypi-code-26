import unittest
import requests
from requests import Session
import json
import httpretty
from dli.client.dli_request_factory_factory import DliRequestFactoryFactory
from dli.client.exceptions import DatalakeException, InsufficientPrivilegeException, UnAuthorisedAccessException

class DliRequestFactoryFactoryTestCase(unittest.TestCase):

    @httpretty.activate
    def test_response_403_raises_InsufficientPrivilegeException(self):
        response_text = 'Insufficient Privileges'
        httpretty.register_uri(httpretty.GET, 'http://dummy.com/test', status=403, body=response_text)

        dli_request_factory_factory = DliRequestFactoryFactory('http://dummy.com')

        with self.assertRaises(InsufficientPrivilegeException):
            response = Session().send(dli_request_factory_factory.request_factory(method='GET', url='/test').prepare())

    @httpretty.activate
    def test_response_401_raises_UnAuthorisedAccessException(self):
        response_text = 'UnAuthorised Access'
        httpretty.register_uri(httpretty.GET, 'http://dummy.com/test', status=401, body=response_text)

        dli_request_factory_factory = DliRequestFactoryFactory('http://dummy.com')

        with self.assertRaises(UnAuthorisedAccessException):
            response = Session().send(dli_request_factory_factory.request_factory(method='GET', url='/test').prepare())

    @httpretty.activate
    def test_response_500_raises_DatalakeException(self):
        response_text = 'Datalake server error'
        httpretty.register_uri(httpretty.GET, 'http://dummy.com/test', status=500, body=response_text)

        dli_request_factory_factory = DliRequestFactoryFactory('http://dummy.com')

        with self.assertRaises(DatalakeException):
            response = Session().send(dli_request_factory_factory.request_factory(method='GET', url='/test').prepare())
