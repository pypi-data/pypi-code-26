from django.test import TestCase
from django.test.client import RequestFactory
from django.conf import settings
from django.core import serializers
from datetime import datetime, timedelta
from authorized.middleware import APIAuthRequestMiddleware
from mock import MagicMock
from authorized.models import Applications
from authorized.views import sample
from authorized import api_utils
import json
import jwt
import time
class AuthorizedAPIMiddlewareTests(TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.path = '/sample'
        self.request.META = {}
        self.request.session = {}
        self.get_response = None
        self.middleware = APIAuthRequestMiddleware(self.get_response)
        Applications.objects.create(name='Dummy', can_request= True)
        Applications.objects.create(name='Random', can_request= False)

    def test_request_without_header(self):
        response = self.middleware.__call__(self.request)
        self.assertEqual(response.status_code, 403)

    def test_request_expired_token(self):
        token = jwt.encode({'app_name': api_utils.get_name(),
                    'exp': datetime.utcnow() + timedelta(seconds=2),
                    'iat': datetime.utcnow(),
                    'nbf': datetime.utcnow()
                    }, 
                    api_utils.get_key(),
                    algorithm='HS512').decode('utf-8')
        time.sleep(3)
        self.request.META['HTTP_APPLICATION_TOKEN'] = token
        response = self.middleware.__call__(self.request)
        self.assertEqual(response.status_code, 500)
    
    def test_request_signed_with_invalid_key(self):
        token = jwt.encode({'app_name': api_utils.get_name(),
                    'exp': datetime.utcnow() + timedelta(seconds=3),
                    'iat': datetime.utcnow(),
                    'nbf': datetime.utcnow()
                    }, 
                    'invalid_key',
                    algorithm='HS512').decode('utf-8')
        self.request.META['HTTP_APPLICATION_TOKEN'] = token
        response = self.middleware.__call__(self.request)
        self.assertEqual(response.status_code, 500)
    
    def test_request_missing_exp_claim(self):
        # missing exp claim
        token = jwt.encode({'app_name': api_utils.get_name(),
                    'iat': datetime.utcnow(),
                    'nbf': datetime.utcnow()
                    }, 
                    api_utils.get_key(),
                    algorithm='HS512').decode('utf-8')
        self.request.META['HTTP_APPLICATION_TOKEN'] = token
        response = self.middleware.__call__(self.request)
        self.assertEqual(response.status_code, 500)

    def test_request_missing_iat_claim(self):
        # missing iat claim
        token = jwt.encode({'app_name': api_utils.get_name(),
                    'exp': datetime.utcnow() + timedelta(seconds=3),
                    'nbf': datetime.utcnow()
                    }, 
                    api_utils.get_key(),
                    algorithm='HS512').decode('utf-8')
        self.request.META['HTTP_APPLICATION_TOKEN'] = token
        response = self.middleware.__call__(self.request)
        self.assertEqual(response.status_code, 500)

    def test_request_missing_nbf_claim(self):
        # missing nbf claim
        token = jwt.encode({'app_name': api_utils.get_name(),
                    'exp': datetime.utcnow() + timedelta(seconds=3),
                    'iat': datetime.utcnow(),
                    },
                    api_utils.get_key(),
                    algorithm='HS512').decode('utf-8')
        self.request.META['HTTP_APPLICATION_TOKEN'] = token
        response = self.middleware.__call__(self.request)
        self.assertEqual(response.status_code, 500)

    def test_request_no_registered_app(self):
        token = jwt.encode({'app_name': 'MRNOBODY',
                    'exp': datetime.utcnow() + timedelta(seconds=2),
                    'iat': datetime.utcnow(),
                    'nbf': datetime.utcnow()
                    }, 
                    api_utils.get_key(),
                    algorithm='HS512').decode('utf-8')
        self.request.META['HTTP_APPLICATION_TOKEN'] = token
        response = self.middleware.__call__(self.request)
        self.assertEqual(response.status_code, 403)

    def test_request_app_with_no_permission(self):
        token = jwt.encode({'app_name': 'Random',
                    'exp': datetime.utcnow() + timedelta(seconds=2),
                    'iat': datetime.utcnow(),
                    'nbf': datetime.utcnow()
                    }, 
                    api_utils.get_key(),
                    algorithm='HS512').decode('utf-8')
        self.request.META['HTTP_APPLICATION_TOKEN'] = token
        response = self.middleware.__call__(self.request)
        self.assertEqual(response.status_code, 403)

    def test_request_with_valid_token(self):
        token = jwt.encode({'app_name': 'Dummy',
                    'exp': datetime.utcnow() + timedelta(seconds=2),
                    'iat': datetime.utcnow(),
                    'nbf': datetime.utcnow()
                    }, 
                    api_utils.get_key(),
                    algorithm='HS512').decode('utf-8')
        mock_header = {}

        mock_header['HTTP_APPLICATION_TOKEN'] = token
        response = self.middleware.process_header(mock_header)
        self.assertEqual(response, True)