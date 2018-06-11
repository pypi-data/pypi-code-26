from django.contrib.auth import get_user_model
from django.test import TestCase, Client


class IndexTest(TestCase):
    fixtures = [
        'initial',
    ]

    def test_not_login(self):
        client = Client()
        resp = client.get('/')
        assert resp.status_code == 200

    def test_logged_in(self):
        client = Client()
        client.force_login(user=get_user_model().objects.first())
        resp = client.get('/')
        assert resp.status_code == 302
