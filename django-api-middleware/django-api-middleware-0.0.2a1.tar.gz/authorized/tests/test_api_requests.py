import requests
from django.test import TestCase
from django.test.utils import override_settings

from authorized import api_request, api_token
from authorized.models import Applications

@override_settings(APP_NAME='Test App')
class CustomRequestsTests(TestCase):

    def setUp(self):
        #for future usage and initial parameters setup
        Applications.objects.create(name='Test App')
        self.header = {'Application-Token': api_token.generate()}
    # Testing response from external source without specifying that is external.
    def test_get_request_ne(self):
        response = api_request.get('https://reqres.in/api/users/', 
                                    params={'id': 1},
                                    headers={'Content-Type':'application/json;charset=UTF-8;'},
                                    cookies=dict(cookies_are='working'))
        self.assertEqual(response.status_code, 599)
    
    def test_head_request_ne(self):
        response = api_request.head('https://reqres.in/api/users/', params={'id': 1})
        self.assertEqual(response.status_code, 599)
    
    def test_options_reqest_ne(self):
        response = api_request.options('https://reqres.in/api/')
        self.assertEqual(response.status_code, 599)
    
    def test_post_request_ne(self):
        response = api_request.post('https://reqres.in/api/users/', 
                                    data={'name': 'morpheus', 'job': 'leader'}, 
                                    headers={'Content-Type':'application/json;charset=UTF-8;'})
        
        self.assertEqual(response.status_code, 599)
    
    def test_put_request_ne(self):
        response = api_request.put('https://reqres.in/api/users/', 
                                    data={'name': 'morpheus', 'job': 'zion resident'}, 
                                    headers={'content-type':'application/json;charset=UTF-8;'})
        self.assertEqual(response.status_code, 599)

    def test_patch_request_ne(self):
        response = api_request.patch('https://reqres.in/api/users/', 
                                    data={'name': 'morpheus', 'job': 'zion resident'}, 
                                    headers={'content-type':'application/json;charset=UTF-8;'})
        self.assertEqual(response.status_code, 599)

    def test_delete_request_ne(self):
        response = api_request.delete('https://reqres.in/api/users/', 
                                    data={'id': 2}, 
                                    headers={'content-type':'application/json;charset=UTF-8;'})
        self.assertEqual(response.status_code, 599)

    # Testing response to external source by placing the request as external
    def test_get_request_e(self):
        response = api_request.get('https://reqres.in/api/users/', 
                                    params={'id': 1},
                                    is_external=True,
                                    headers={'Content-Type':'application/json;charset=UTF-8;'},
                                    cookies=dict(cookies_are='working'))
        self.assertEqual(response.status_code, 200)
    
    def test_head_request_e(self):
        response = api_request.head('https://reqres.in/api/users/', params={'id': 1}, is_external=True)
        self.assertEqual(response.status_code, 200)
    
    def test_options_reqest_e(self):
        response = api_request.options('https://reqres.in/api/', is_external=True)
        self.assertEqual(response.status_code, 204)
    
    def test_post_request_e(self):
        response = api_request.post('https://reqres.in/api/users/', 
                                    data={'name': 'morpheus', 'job': 'leader'},
                                    is_external=True, 
                                    headers={'Content-Type':'application/json;charset=UTF-8;'})
        
        self.assertEqual(response.status_code, 201)
    
    def test_put_request_e(self):
        response = api_request.put('https://reqres.in/api/users/', 
                                    data={'name': 'morpheus', 'job': 'zion resident'},
                                    is_external=True,
                                    headers={'content-type':'application/json;charset=UTF-8;'})
        self.assertEqual(response.status_code, 200)

    def test_patch_request_e(self):
        response = api_request.patch('https://reqres.in/api/users/', 
                                    is_external=True,
                                    data={'name': 'morpheus', 'job': 'zion resident'}, 
                                    headers={'content-type':'application/json;charset=UTF-8;'})
        self.assertEqual(response.status_code, 200)

    def test_delete_request_e(self):
        response = api_request.delete('https://reqres.in/api/users/', 
                                    data={'id': 2},
                                    is_external=True,
                                    headers={'content-type':'application/json;charset=UTF-8;'})
        self.assertEqual(response.status_code, 204)

    # Test that verifies a 'forced response header' to check that it will verifies if the token is accepted or not.
    # using python requests library and then forcing a header.
    def test_get_request(self):
        response = requests.get('https://reqres.in/api/users/', 
                                    params={'id': 1},
                                    headers={'Content-Type':'application/json;charset=UTF-8;'},
                                    cookies=dict(cookies_are='working'))
        response.headers.update(self.header)
        self.assertEqual(api_request.process_response_header(response).status_code, 200)
    
    def test_head_request(self):
        response = requests.head('https://reqres.in/api/users/', params={'id': 1})
        response.headers.update(self.header)
        self.assertEqual(api_request.process_response_header(response).status_code, 200)
    
    def test_options_reqest(self):
        response = requests.options('https://reqres.in/api/')
        response.headers.update(self.header)
        self.assertEqual(api_request.process_response_header(response).status_code, 204)
    
    def test_post_request(self):
        response = requests.post('https://reqres.in/api/users/', 
                                    data={'name': 'morpheus', 'job': 'leader'},
                                    headers={'Content-Type':'application/json;charset=UTF-8;'})
        response.headers.update(self.header)
        self.assertEqual(api_request.process_response_header(response).status_code, 201)
    
    def test_put_request(self):
        response = requests.put('https://reqres.in/api/users/', 
                                    data={'name': 'morpheus', 'job': 'zion resident'},
                                    headers={'content-type':'application/json;charset=UTF-8;'})
        response.headers.update(self.header)
        self.assertEqual(api_request.process_response_header(response).status_code, 200)

    def test_patch_request(self):
        response = requests.patch('https://reqres.in/api/users/',
                                    data={'name': 'morpheus', 'job': 'zion resident'}, 
                                    headers={'content-type':'application/json;charset=UTF-8;'})
        response.headers.update(self.header)
        self.assertEqual(api_request.process_response_header(response).status_code, 200)

    def test_delete_request(self):
        response = requests.delete('https://reqres.in/api/users/', 
                                    data={'id': 2},
                                    headers={'content-type':'application/json;charset=UTF-8;'})
        response.headers.update(self.header)
        self.assertEqual(api_request.process_response_header(response).status_code, 204)
