import json

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.test.testcases import TestCase

from .models import OAuthToken, OAuthService, GroupManagerConnection, DDSEndpoint, DDSUserCredential


class OAuthTokenTest(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create(username='user1')
        self.service = OAuthService.objects.create(name='service1',
                                                   client_id='id123',
                                                   client_secret='secret456',
                                                   redirect_uri='https://redirect/',
                                                   scope='scope1',
                                                   authorization_uri='https://authorize/',
                                                   token_uri='https://token/')
        self.token_dict = {'token': 'abc123'}
        self.token_json = json.dumps(self.token_dict)

    def test_token_types(self):
        self.assertEqual(type(self.token_dict), dict, 'token dict is dict')
        self.assertEqual(type(self.token_json), str, 'token json is string')

    def test_create_token(self):
        t = OAuthToken.objects.create(user=self.user, service=self.service, token_json=self.token_json)
        self.assertEqual(t.user, self.user, 'sets user')
        self.assertEqual(t.service, self.service, 'sets service')
        self.assertEqual(t.token_json, self.token_json, 'sets json')

    def test_requires_unique_user_service(self):
        OAuthToken.objects.create(user=self.user, service=self.service, token_json=self.token_json)
        with self.assertRaises(IntegrityError):
            OAuthToken.objects.create(user=self.user, service=self.service, token_json='{}')

    def test_requires_unique_service_token(self):
        OAuthToken.objects.create(user=self.user, service=self.service, token_json=self.token_json)
        user2 = get_user_model().objects.create(username='user2')
        with self.assertRaises(IntegrityError):
            OAuthToken.objects.create(user=user2, service=self.service, token_json=self.token_json)

    def test_allows_duplicate_user_token(self):
        # User and token may be the same if service is different
        t1 = OAuthToken.objects.create(user=self.user, service=self.service, token_json=self.token_json)
        service2 = OAuthService.objects.create(name='service2',
                                               client_id='id456',
                                               client_secret='secret222',
                                               redirect_uri='https://redirect2/',
                                               scope='scope2',
                                               authorization_uri='https://authorize2/',
                                               token_uri='https://token2/')
        t2 = OAuthToken.objects.create(user=self.user, service=service2, token_json=self.token_json)
        self.assertNotEqual(t1.service, t2.service, 'Services are unique')
        self.assertEqual(t1.user, t2.user, 'Users are identical')
        self.assertEqual(t1.token_json, t2.token_json, 'Token jsons are identical')

    def test_deserialize_json(self):
        t = OAuthToken.objects.create(user=self.user, service=self.service, token_json=self.token_json)
        self.assertEqual(t.token_dict, self.token_dict, 'De-serializes JSON from string')

    def test_serialize_json(self):
        t = OAuthToken.objects.create(user=self.user, service=self.service)
        t.token_dict = self.token_dict
        t.save()
        self.assertEqual(t.token_json, self.token_json)


class GroupManagerConnectionTest(TestCase):
    def test_create_and_read(self):
        self.assertEqual(0, len(GroupManagerConnection.objects.all()),
                         "There should be no connections by default")
        gmc = GroupManagerConnection.objects.create(account_id='123', password='abc')
        self.assertIsNotNone(gmc.base_url,
                             "Base url should have a default value")
        gmc = GroupManagerConnection.objects.first()
        self.assertEqual(gmc.account_id, 123,
                         "GroupManagerConnection should save account_id as an integer")
        self.assertEqual(gmc.password, 'abc',
                         "GroupManagerConnection should save password")


class DDSEndpointTestCase(TestCase):

    def test_unique_name(self):
        DDSEndpoint.objects.create(name='name1')
        with self.assertRaises(IntegrityError):
            DDSEndpoint.objects.create(name='name1')

    def test_unique_agent_key(self):
        DDSEndpoint.objects.create(agent_key='key1')
        with self.assertRaises(IntegrityError):
            DDSEndpoint.objects.create(agent_key='key1')

    def test_validates_blank_fields(self):
        endpoint = DDSEndpoint.objects.create()
        with self.assertRaises(ValidationError) as e:
            endpoint.clean_fields()
        error_keys = e.exception.error_dict.keys()
        self.assertSetEqual(set(error_keys),
                            {'name','agent_key','portal_root','api_root','openid_provider_id'})

    def test_unique_parameters1(self):
        endpoint1 = DDSEndpoint.objects.create(name='endpoint1', agent_key='abc123')
        self.assertIsNotNone(endpoint1)
        endpoint2 = DDSEndpoint.objects.create(name='endpoint2', agent_key='def456')
        self.assertIsNotNone(endpoint2)
        self.assertNotEqual(endpoint1, endpoint2)
        with self.assertRaises(IntegrityError):
            DDSEndpoint.objects.create(name='endpoint3', agent_key=endpoint1.agent_key)


class DDSUserCredentialTestCase(TestCase):

    def setUp(self):
        self.endpoint1 = DDSEndpoint.objects.create(name='endpoint1',
                                                    api_root='https://example1.org/api',
                                                    portal_root='https://example2.org',
                                                    openid_provider_id='abc123',
                                                    agent_key='dds123')
        self.endpoint2 = DDSEndpoint.objects.create(name='endpoint2',
                                                    api_root='https://example2.org/api',
                                                    portal_root='https://example2.org',
                                                    openid_provider_id='def456',
                                                    agent_key='fef332')
        User = get_user_model()
        self.user1 = User.objects.create(username='user1')
        self.user2 = User.objects.create(username='user2')

    def test_creates_with_user_and_endpoint(self):
        DDSUserCredential.objects.create(user=self.user1, endpoint=self.endpoint1)

    def test_requires_user_relationship(self):
        with self.assertRaises(IntegrityError) as e:
            DDSUserCredential.objects.create(user=None, endpoint=self.endpoint1)

    def test_requires_endpoint_relationship(self):
        with self.assertRaises(IntegrityError) as e:
            DDSUserCredential.objects.create(user=self.user1, endpoint=None)

    def test_unique_token(self):
        DDSUserCredential.objects.create(user=self.user1, endpoint=self.endpoint1, token='token1')
        with self.assertRaises(IntegrityError):
            DDSUserCredential.objects.create(user=self.user1, endpoint=self.endpoint1, token='token1')

    def test_unique_dds_id(self):
        DDSUserCredential.objects.create(user=self.user1, endpoint=self.endpoint1, dds_id='dds_id1')
        with self.assertRaises(IntegrityError):
            DDSUserCredential.objects.create(user=self.user1, endpoint=self.endpoint1, dds_id='dds_id1')

    def test_unique_endpoint_and_user(self):
        DDSUserCredential.objects.create(endpoint=self.endpoint1, user=self.user1, dds_id='dds_id1', token='token1')
        DDSUserCredential.objects.create(endpoint=self.endpoint1, user=self.user2, dds_id='dds_id2', token='token2')
        with self.assertRaises(IntegrityError):
            DDSUserCredential.objects.create(endpoint=self.endpoint1, user=self.user1, dds_id='dds_id3', token='token3')

    def test_user_can_have_creds_for_diff_endpoints(self):
        DDSUserCredential.objects.create(user=self.user1, token='abc123', endpoint=self.endpoint1, dds_id='1')
        DDSUserCredential.objects.create(user=self.user1, token='abc124', endpoint=self.endpoint2, dds_id='2')
