"""
Test pubsub abstraction
"""
from backends import PubNubBackend
from pubsub import get_backend
import unittest


class TestPubSubAbstractionBackend(unittest.TestCase):

    def setUp(self):
        self.pubsub = get_backend('backends', 'PubNubBackend', 'test-channel')

    def test_backend_is_instance_of_class(self):
        assert isinstance(self.pubsub, PubNubBackend)

    def test_provides_required_functions(self):
        required_methods = ['publish', 'subscribe']
        for method in required_methods:
            assert getattr(self.pubsub, method, None) is not None


if __name__ == '__main__':
    unittest.main()
