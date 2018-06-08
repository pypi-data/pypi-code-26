# Copyright 2018 Globo.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Tests for the faasclient.client.get_keystone_auth method """

import sys
import unittest

from keystoneclient import exceptions as ksexceptions
from mock import patch, Mock

from faasclient.client import get_keystone_auth, _discover_auth_version, \
    _import_keystone_client
from faasclient.exceptions import ClientException


class TestGetAuth(unittest.TestCase):

    def setUp(self):
        self.ksclient = Mock()
        patch('faasclient.client._import_keystone_client', Mock(
            return_value=self.ksclient)).start()

    def tearDown(self):
        patch.stopall()

    def test_get_keystone_auth_called_with_minimum_parameters(self):
        """
        Verify if get_keystone_auth calls keystone.Client with right parameters
        """

        get_keystone_auth('https://localhost/v2.0', 'user', 'key', {})

        self.ksclient.Client.assert_called_with(
            username='user',
            password='key',
            token=None,
            tenant_name=None,
            tenant_id=None,
            user_id=None,
            user_domain_name=None,
            user_domain_id=None,
            project_name=None,
            project_id=None,
            project_domain_name=None,
            project_domain_id=None,
            debug=False,
            auth_url='https://localhost/v2.0',
            insecure=False,
            timeout=None)

        service_catalog = self.ksclient.Client.return_value.service_catalog
        service_catalog.url_for.assert_called_with(
            service_type='block-storage',
            endpoint_type='adminURL')

    def test_get_keystone_auth_called_with_all_parameters(self):
        """
        Verify if get_keystone_auth calls keystone.Client with right parameters
        """

        os_options = {
            'token': '1234567890',
            'tenant_name': 'tenant_name',
            'tenant_id': '11223344',
            'user_id': '44112233',
            'user_domain_name': 'user_domain_name',
            'user_domain_id': '0987654321',
            'project_name': 'project_name',
            'project_id': '12211221',
            'project_domain_name': 'project_domain_name',
            'project_domain_id': '45454545',
        }

        get_keystone_auth('https://localhost/v2.0', 'user', 'key', os_options,
                          insecure=True, timeout=5)

        self.ksclient.Client.assert_called_with(
            username='user',
            password='key',
            token=os_options.get('auth_token'),
            tenant_name=os_options.get('tenant_name'),
            tenant_id=os_options.get('tenant_id'),
            user_id=os_options.get('user_id'),
            user_domain_name=os_options.get('user_domain_name'),
            user_domain_id=os_options.get('user_domain_id'),
            project_name=os_options.get('project_name'),
            project_id=os_options.get('project_id'),
            project_domain_name=os_options.get('project_domain_name'),
            project_domain_id=os_options.get('project_domain_id'),
            debug=False,
            auth_url='https://localhost/v2.0',
            insecure=True,
            timeout=5)

    def test_get_keystone_auth_return_values(self):
        """
        Verify if get_keystone_auth returns the proper token and endpoint
        """

        expected_endpoint = 'https://localhost:5000/v2.0'
        expected_token = '1234567890'

        self.ksclient.Client.return_value.auth_token = expected_token
        self.ksclient.Client.return_value.service_catalog.url_for\
            .return_value = expected_endpoint

        computed_enpoint, computed_token = get_keystone_auth(
            'https://localhost:5000/v2.0', 'user', 'key', {})

        self.assertEqual(expected_endpoint, computed_enpoint)
        self.assertEqual(expected_token, computed_token)

    def test_get_keystone_auth_not_authorized(self):
        """
        Verify if get_keystone_auth raises ClientException with the proper
        message when the authentication is denied
        """

        self.ksclient.Client.side_effect = ksexceptions.Unauthorized

        with self.assertRaises(ClientException) as excpt:
            get_keystone_auth('https://localhost/v2.0', 'user', 'key', {})

        expected = 'Unauthorized. Check username, password and tenant name/id.'
        computed = str(excpt.exception)

        self.assertEqual(expected, computed)

    def test_get_keystone_auth_authorization_failure(self):
        """
        Verify if get_keystone_auth raises ClientException with the proper
        message when the authentication fails
        """

        self.ksclient.Client.side_effect = ksexceptions.AuthorizationFailure(
            'Falha!')

        with self.assertRaises(ClientException) as excpt:
            get_keystone_auth('https://localhost/v2.0', 'user', 'key', {})

        expected = 'Authorization Failure. Falha!'
        computed = str(excpt.exception)

        self.assertEqual(expected, computed)

    def test_get_keystone_auth_endpoint_not_found(self):
        """
        Verify if get_keystone_auth raises ClientException if the
        os_options['endpoint_type'] and/or the os_options['service_type'] do
        not exists in the auth response
        """

        self.ksclient.Client.return_value\
            .service_catalog\
            .url_for\
            .side_effect = ksexceptions.EndpointNotFound

        with self.assertRaises(ClientException) as excpt:
            get_keystone_auth('https://localhost/v2.0', 'user', 'key', {})

        expected = ('Endpoint for block-storage not found'
                    ' - have you specified a region?')
        computed = str(excpt.exception)

        self.assertEqual(expected, computed)

    def test_discover_auth_version(self):

        version = _discover_auth_version('https://localhost:5000/v2.0')
        self.assertEqual(version, 2)

        version = _discover_auth_version('https://localhost:5000/v3')
        self.assertEqual(version, 3)

    def test_import_keystone_client_v2(self):

        _import_keystone_client(2)
        self.assertIn('keystoneclient.v2_0', sys.modules)

    def test_import_keystone_client_v3(self):

        _import_keystone_client(3)
        self.assertIn('keystoneclient.v3', sys.modules)

    def test_import_keystone_client_invalid_version(self):
        """ Default version loaded is v2 """

        _import_keystone_client('invalid')
        self.assertIn('keystoneclient.v2_0', sys.modules)


if __name__ == '__main__':
    unittest.main()