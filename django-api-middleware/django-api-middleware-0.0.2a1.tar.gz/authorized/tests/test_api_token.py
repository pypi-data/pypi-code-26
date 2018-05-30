from django.test import TestCase
from authorized import api_token
class APITokenTests(TestCase):
    def setUp(self):
        pass
    
    def test_generate_token(self):
        token = api_token.generate()
        self.assertIsNotNone(token,None)
    
    def test_verify_token(self):
        token = api_token.generate()
        verified_token = api_token.verify(token)
        self.assertEqual(verified_token['is_valid'], True)
    