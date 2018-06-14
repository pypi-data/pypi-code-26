from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from requests.auth import HTTPBasicAuth
from django.conf import settings


class JWTViewsTestCase(APITestCase):

    def test_fails_when_logged_out(self):
        self.client.logout()
        response = self.client.post(reverse('auth-api-token-session'), {})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")

    def test_fails_with_non_session_authentication(self):
        # Will try HTTP Basic Authentication, make sure that's elected in the settings
        self.assertIn('rest_framework.authentication.BasicAuthentication', settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'])
        user = get_user_model().objects.create(username='user', password='pass')
        self.client.auth = HTTPBasicAuth('user', 'pass')
        response = self.client.post(reverse('auth-api-token-session'), {})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")

    def test_succeeds_with_session_authentication(self):
        get_user_model().objects.create_user(username='user', password='pass')
        self.client.login(username='user', password='pass')
        response = self.client.post(reverse('auth-api-token-session'), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
