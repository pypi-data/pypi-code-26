import unittest

from goodreads_api_client.transport import Transport
from goodreads_api_client.tests.conftest import (
    developer_key, developer_secret)


class TestTransport(unittest.TestCase):
    def test_init_default(self):
        transport = Transport(developer_key=developer_key,
                              developer_secret=developer_secret,
                              base_url='http://example.com')

        self.assertEqual(transport.base_url, 'http://example.com')

    def test_init_override(self):
        transport = Transport(developer_key=developer_key,
                              developer_secret=developer_secret)

        self.assertEqual(transport.base_url, 'http://www.goodreads.com')
