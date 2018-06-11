import unittest

from ..error_handlers import is_attribute_set

class MockClass(object):

    @is_attribute_set('name')
    def fake_method(self):
        return 3

class TestAttributesSet(unittest.TestCase):
    def setUp(self):
        self.MOCKCLASS = MockClass()

    def test_set_up(self):
        self.assertRaises(AttributeError, self.MOCKCLASS.fake_method)

    def test_returns_val_if_attribute_set(self):
        self.MOCKCLASS.name = 'fake'
        self.assertEqual(3, self.MOCKCLASS.fake_method())
