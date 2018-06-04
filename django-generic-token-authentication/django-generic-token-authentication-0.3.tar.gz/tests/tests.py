from django.test import TestCase, TransactionTestCase

class GenericFunctionsTest(TransactionTestCase):
    def test_generic(self):
        self.assertEqual(True, True)