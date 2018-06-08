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

import re
import json
import logging
import requests
from urlparse import urlparse
from keystoneclient import exceptions as ksexceptions
from faasclient.exceptions import ClientException


try:
    from logging import NullHandler
except ImportError:
    # Added in Python 2.7
    class NullHandler(logging.Handler):
        def handle(self, record):
            pass

        def emit(self, record):
            pass

        def createLock(self):
            self.lock = None


logger = logging.getLogger('faasclient')


class Client(object):

    def __init__(self, authurl=None, user=None, key=None, preauthurl=None,
                 preauthtoken=None, tenant_name=None, os_options=None,
                 insecure=False):
        """
        :param authurl: authentication URL
        :param user: user name to authenticate as
        :param key: key/password to authenticate with
        :param retries: Number of times to retry the request before failing
        :param preauthurl: storage URL (if you have already authenticated)
        :param preauthtoken: authentication token (if you have already
                             authenticated) note authurl/user/key/tenant_name
                             are not required when specifying preauthtoken
        :param tenant_name: The tenant/account name, required when connecting
                            to an auth 2.0 system.
        :param os_options: The OpenStack options which can have tenant_id,
                           auth_token, service_type, endpoint_type,
                           tenant_name, block_storage_url, region_name,
                           service_username, service_project_name, service_key
        :param insecure: Allow to access servers without checking SSL certs.
                         The server's certificate will not be verified.
        """
        self.authurl = authurl
        self.user = user
        self.key = key
        self.http_conn = None
        self.attempts = 0
        self.os_options = dict(os_options or {})
        if tenant_name:
            self.os_options['tenant_name'] = tenant_name
        if preauthurl:
            self.os_options['block_storage_url'] = preauthurl

        self.url = preauthurl or self.os_options.get('block_storage_url')
        self.token = preauthtoken or self.os_options.get('auth_token')

        if self.os_options.get('service_username', None):
            self.service_auth = True
        else:
            self.service_auth = False
        self.service_token = None
        self.insecure = insecure

    # AUTENTICACAO  ------------------------------------------------------------
    def get_auth(self):
        url, token = get_keystone_auth(self.authurl, self.user, self.key,
                                       os_options=self.os_options,
                                       insecure=self.insecure)
        return url, token

    # ACCESS  ------------------------------------------------------------------
    def access_list(self, export_id_or_path):
        url_path = '/exports/{}/hosts'.format(export_id_or_path)

        return self._get_request(url_path)

    def access_delete(self, export_id_or_path, access_id, audit=False):
        url_path = '/exports/{}/hosts/{}'.format(export_id_or_path, access_id)

        return self._delete_request(url_path, audit=audit)

    def access_get(self, export_id_or_path, access_id):
        url_path = '/exports/{}/hosts/{}'.format(export_id_or_path, access_id)

        return self._get_request(url_path)

    def access_create(self, export_id_or_path, permission, host, audit=False):
        url_path = '/exports/{}/hosts'.format(export_id_or_path)
        data = {'permission': permission, 'host': host}

        return self._post_request(url_path, data, audit=audit)

    # CATEGORIA  ---------------------------------------------------------------
    def categoria_list(self):
        url_path = '/categorias'

        return self._get_request(url_path)

    def categoria_get(self, categoria_id):
        url_path = '/categorias/{}'.format(categoria_id)

        return self._get_request(url_path)

    def categoria_create(self, name):
        url_path = '/categorias'
        data = {'name': name}

        return self._post_request(url_path, data)

    def categoria_update(self, categoria_id, name):
        url_path = '/categorias/{}'.format(categoria_id)
        data = {'name': name}

        return self._put_request(url_path, data)

    def categoria_delete(self, categoria_id):
        url_path = '/categorias/{}'.format(categoria_id)

        return self._delete_request(url_path)

    # AUDIT  -------------------------------------------------------------------
    def audit_list(self):
        url_path = '/audits'

        return self._get_request(url_path)

    def audit_get(self, audit_id):
        url_path = '/audits/{}'.format(audit_id)

        return self._get_request(url_path)

    def audit_export_get(self, export_id):
        url_path = '/audits/export/{}'.format(export_id)

        return self._get_request(url_path)

    # APPHOST  ------------------------------------------------------------
    def apphost_list(self):
        url_path = '/apphosts'

        return self._get_request(url_path)

    def apphost_create(self, ip, hostname):
        url_path = '/apphosts'
        data = {'ip': ip, 'hostname': hostname}

        return self._post_request(url_path, data)

    def apphost_get(self, conf_id):
        url_path = '/apphosts/{}'.format(conf_id)
        return self._get_request(url_path)

    def apphost_delete(self, conf_id):
        url_path = '/apphosts/{}'.format(conf_id)

        return self._delete_request(url_path)

    def apphost_update(self, conf_id, ip, hostname):
        url_path = '/apphosts/{}'.format(conf_id)
        data = {'ip': ip, 'hostname': hostname}

        return self._put_request(url_path, data)

    # EXPORT  ------------------------------------------------------------------
    def project_quota_get(self):
        url_path = '/quota'
        return self._get_request(url_path)

    def export_get(self, export_id_or_path):
        url_path = '/exports/{}'.format(export_id_or_path)
        return self._get_request(url_path)

    def export_list(self, host=None):
        if host:
            url_path = '/exports?host={}'.format(host)
        else:
            url_path = '/exports'
        return self._get_request(url_path)

    def export_create(self, quota, categoria, resource_id=None, time_id=None, audit=False):
        url_path = '/exports'
        data = {'quota': quota, 'categoria': categoria, 'resource_id': resource_id, 'time_id': time_id}
        
        return self._post_request(url_path, data, audit=audit)

    def export_delete(self, export_id_or_path, audit=False):
        url_path = '/exports/{}'.format(export_id_or_path)
        return self._delete_request(url_path, audit=audit)

    def export_force_delete(self, export_id_or_path, audit=False):
        url_path = '/exports/{}/force'.format(export_id_or_path)
        return self._delete_request(url_path, audit=audit)

    def export_update(self, export_id_or_path, quota, audit=False):
        url_path = '/exports/{}'.format(export_id_or_path)
        data = {'quota': quota}

        return self._put_request(url_path, data, audit=audit)

    def export_group(self, exports_id, resource_id, audit=False):
        url_path = '/exports/resource'
        data = {'exports': exports_id, 'resource_id': resource_id}
        
        return self._post_request(url_path, data, audit=audit)

    def exports_time(self, exports_id, time_id, audit=False):
        url_path = '/exports/time'
        data = {'exports': exports_id, 'time_id': time_id}
        
        return self._post_request(url_path, data, audit=audit)

    # FILER  ------------------------------------------------------------------
    def filer_list(self):
        url_path = '/filers'

        return self._get_request(url_path)

    def filer_create(self, vfiler, export_filer, connection_filer, username,
                     password):
        url_path = '/filers'
        data = {
            'vfiler': vfiler,
            'export_filer': export_filer,
            'connection_filer': connection_filer,
            'username': username,
            'password': password,
        }

        return self._post_request(url_path, data)

    def filer_get(self, filer_id):
        url_path = '/filers/{}'.format(filer_id)

        return self._get_request(url_path)

    def filer_delete(self, filer_id):
        url_path = '/filers/{}'.format(filer_id)

        return self._delete_request(url_path)

    def filer_update(self, filer_id, vfiler, export_filer, connection_filer,
                     username, password):
        url_path = '/filers/{}'.format(filer_id)
        data = {
            'vfiler': vfiler,
            'export_filer': export_filer,
            'connection_filer': connection_filer,
            'username': username,
            'password': password,
        }

        return self._put_request(url_path, data)

    # VOLUME  ------------------------------------------------------------------
    def volume_list(self):
        url_path = '/volumes'

        return self._get_request(url_path)

    def volume_create(self, path, filer_id, categoria_id, maxsnapshots):
        url_path = '/volumes'
        data = {
            'path': path,
            'filer_id': filer_id,
            'categoria_id': categoria_id,
            'maxsnapshots': maxsnapshots,
        }

        return self._post_request(url_path, data)

    def volume_get(self, volume_id):
        url_path = '/volumes/{}'.format(volume_id)

        return self._get_request(url_path)

    def volume_delete(self, volume_id):
        url_path = '/volumes/{}'.format(volume_id)

        return self._delete_request(url_path)

    def volume_update(self, volume_id, path, filer_id, categoria_id,
                      maxsnapshots):
        url_path = '/volumes/{}'.format(volume_id)
        data = {
            'path': path,
            'filer_id': filer_id,
            'categoria_id': categoria_id,
            'maxsnapshots': maxsnapshots,
        }

        return self._put_request(url_path, data)

    def volumes_info(self):
        url_path = '/volumes-info'

        return self._get_request(url_path)

    def volumes_update_info(self):
        url_path = '/volumes-info-update'

        return self._post_request(url_path)

    # PERMISSAO  ---------------------------------------------------------------
    def permission_list(self):
        url_path = '/permissions'

        return self._get_request(url_path)

    def permission_create(self, name):
        url_path = '/permissions'
        data = {'name': name}

        return self._post_request(url_path, data)

    def permission_get(self, permission_id):
        url_path = '/permissions/{}'.format(permission_id)
        return self._get_request(url_path)

    def permission_delete(self, permission_id):
        url_path = '/permissions/{}'.format(permission_id)

        return self._delete_request(url_path)

    def permission_update(self, permission_id, name):
        url_path = '/permissions/{}'.format(permission_id)
        data = {'name': name}

        return self._put_request(url_path, data)

    # QUOTA  -------------------------------------------------------------------
    def quota_get(self, export_id=None):
        if export_id:
            url_path = '/exports/{}/quota'.format(export_id)
        else:
            url_path = '/quota'

        return self._get_request(url_path)

    def quota_post(self, export_id, size):
        url_path = '/exports/{}/quota'.format(export_id)
        data = {'size': size}

        return self._post_request(url_path, data)

    def quota_delete(self, export_id):
        url_path = '/exports/{}/quota'.format(export_id)

        return self._delete_request(url_path)

    # RESTORE / JOBS  ----------------------------------------------------------
    def jobs_list(self):
        url_path = '/restore/jobs'

        return self._get_request(url_path)

    def jobs_get(self, job_id):
        url_path = '/restore/jobs/{}'.format(job_id)

        return self._get_request(url_path)

    # SNAPSHOTS  ---------------------------------------------------------------
    def snapshot_list(self, export_id_or_path):
        url_path = '/exports/{}/snapshots'.format(export_id_or_path)

        return self._get_request(url_path)

    def snapshot_delete(self, export_id_or_path, snapshot_id, audit=False):
        url_path = '/exports/{}/snapshots/{}'.format(export_id_or_path, snapshot_id)

        return self._delete_request(url_path, audit=audit)

    def snapshot_get(self, export_id_or_path, snapshot_id):
        url_path = '/exports/{}/snapshots/{}'.format(export_id_or_path, snapshot_id)

        return self._get_request(url_path)

    def snapshot_create(self, export_id_or_path, audit=False):
        url_path = '/exports/{}/snapshots'.format(export_id_or_path)

        return self._post_request(url_path, audit=audit)

    def snapshot_restore(self, export_id_or_path, snapshot_id, audit=False):
        url_path = '/exports/{}/snapshots/{}/restore'.format(export_id_or_path, snapshot_id)

        return self._post_request(url_path, audit=audit)

    # REPORT TO GLOBOMAP  ---------------------------------------------------------------
    def report_get(self):
        url_path = '/report'

        return self._get_request(url_path)

    # REQUESTS
    def _request(self, method, url_path, data=None, headers=None, audit=False):

        if not self.token:
            project_url, self.token = self.get_auth()

        if self.url is None:
            self.url = project_url

        headers = headers or {}  # Case headers is None
        headers['X-Storage-Token'] = self.token
        url = self.url + url_path

        if url_path == '/report':
            parsed = urlparse(self.url)
            
            url = '{}://{}{}'.format(parsed.scheme, parsed.hostname, url_path)

        r = requests.request(method, url, data=data, headers=headers,
                             verify=not self.insecure)
        
        if audit:
            return r
        
        try:
            response = r.json()
        except ValueError:
            response = ''
        
        return r.status_code, response

    def _get_request(self, url_path, headers=None):
        return self._request('get', url_path, headers=headers)

    def _post_request(self, url_path, data=None, headers=None, audit=False):
        
        return self._request('post', url_path, data=data, headers=headers, audit=audit)

    def _put_request(self, url_path, data, headers=None, audit=False):
        return self._request('put', url_path, data=data, headers=headers, audit=audit)

    def _delete_request(self, url_path, headers=None, audit=False):
        return self._request('delete', url_path, headers=headers, audit=audit)


def _import_keystone_client(auth_version):
    """
    Import the proper keystoneclient for a specific version. If a invalid
    version is requests, version 2 will be loaded.

    Based on:
    https://github.com/openstack/python-swiftclient/blob/
    307d4c007afaccdcd70628d9fce44231115d62cd/swiftclient/client.py#L522
    """

    try:
        if auth_version in ('3.0', '3', 3):
            from keystoneclient.v3 import client as ksclient
        else:
            from keystoneclient.v2_0 import client as ksclient

        # prevent keystoneclient warning us that it has no log handlers
        logging.getLogger('keystoneclient').addHandler(NullHandler())

        return ksclient
    except ImportError:
        raise ClientException('''
Auth versions 2.0 and 3 require python-keystoneclient, install it or use Auth
version 1.0 which requires ST_AUTH, ST_USER, and ST_KEY environment
variables to be set or overridden with -A, -U, or -K.''')


def _discover_auth_version(auth_url):
    # Return the auth version (2 or 3) based on auth_url parameter
    # Ex.: https://domain:port/v2.0 => 2
    #      https://domain:port/v3   => 3

    if auth_url is None:
        raise ClientException('Unknown Auth URL')

    version = 'v2.0'
    try:
        version = auth_url.split('/')[3]
    except IndexError:
        ClientException('Unknown Auth version')

    if version in ('v3', 'v3.0', '3'):
        return 3

    return 2


def get_keystone_auth(auth_url, user, key, os_options, **kwargs):
    """
    Authenticate against a keystone server.
    We are using the keystoneclient library for authentication.
    """

    insecure = kwargs.get('insecure', False)
    timeout = kwargs.get('timeout', None)
    debug = logger.isEnabledFor(logging.DEBUG)

    auth_version = _discover_auth_version(auth_url)

    ksclient = _import_keystone_client(auth_version)

    try:
        _ksclient = ksclient.Client(
            username=user,
            password=key,
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
            debug=debug,
            auth_url=auth_url, insecure=insecure, timeout=timeout)
    except ksexceptions.Unauthorized:
        msg = 'Unauthorized. Check username, password and tenant name/id.'
        raise ClientException(msg)
    except ksexceptions.AuthorizationFailure as err:
        raise ClientException('Authorization Failure. %s' % err)

    service_type = os_options.get('service_type') or 'block-storage'
    endpoint_type = os_options.get('endpoint_type') or 'adminURL'

    try:
        filter_kwargs = {}
        if os_options.get('region_name'):
            filter_kwargs['attr'] = 'region'
            filter_kwargs['filter_value'] = os_options['region_name']

        endpoint = _ksclient.service_catalog.url_for(
            service_type=service_type,
            endpoint_type=endpoint_type,
            **filter_kwargs)
    except ksexceptions.EndpointNotFound:
        raise ClientException('Endpoint for %s not found - '
                              'have you specified a region?' % service_type)

    return endpoint, _ksclient.auth_token
