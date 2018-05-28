import unittest
from unittest.mock import patch

import requests
from goodreads_api_client.tests.conftest import developer_key, developer_secret
from goodreads_api_client.transport import Transport


class ResourceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run both child class setup, as well as this class setup.

        Taken from https://gist.github.com/twolfson/13f5f5784f67fd49b245.
        """
        if cls is not ResourceTestCase and \
                cls.setUp is not ResourceTestCase.setUp:
            child_setup = cls.setUp

            def merged_setup(self, *args, **kwargs):
                ResourceTestCase.setUp(self)
                return child_setup(self, *args, **kwargs)

            cls.setUp = merged_setup

    def setUp(self):
        self._transport = Transport(developer_key=developer_key,
                                    developer_secret=developer_secret)

        patch_transport = patch.object(Transport, 'session', requests)
        patch_transport.start()

        self.addCleanup(patch_transport.stop)

        if self._transport.is_using_session():
            self.addCleanup(self._transport.session.close)
