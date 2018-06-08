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

""" Tests for faasclient.client methods """

import unittest
from mock import patch
from faasclient.client import Client


class TestFaasclient(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    # REQUESTS
    # ---------------------------------------------------------------------
    @patch('faasclient.client.Client._request')
    def test_get_request(self, mock_request):

        url_path = '/some/path'

        self.client._get_request(url_path)
        mock_request.assert_called_with('get', url_path, headers=None)

        header = {'header': 'value'}

        self.client._get_request(url_path, headers=header)
        mock_request.assert_called_with('get', url_path, headers=header)

    @patch('faasclient.client.Client._request')
    def test_post_request(self, mock_request):

        url_path = '/some/path'
        data = {'name': 'any name'}

        self.client._post_request(url_path, data)
        mock_request.assert_called_with('post', url_path, data=data,
                                        headers=None, audit=False)

        header = {'header': 'value'}

        self.client._post_request(url_path, data, headers=header)
        mock_request.assert_called_with('post', url_path, data=data,
                                        headers=header, audit=False)

    @patch('faasclient.client.Client._request')
    def test_put_request(self, mock_request):

        url_path = '/some/path'
        data = {'name': 'any name'}

        self.client._put_request(url_path, data)
        mock_request.assert_called_with('put', url_path, data=data,
                                        headers=None, audit=False)

        header = {'header': 'value'}

        self.client._put_request(url_path, data, headers=header)
        mock_request.assert_called_with('put', url_path, data=data,
                                        headers=header, audit=False)

    @patch('faasclient.client.Client._request')
    def test_delete_request(self, mock_request):

        url_path = '/some/path'

        self.client._delete_request(url_path)
        mock_request.assert_called_with('delete', url_path, audit=False, headers=None)

        header = {'header': 'value'}

        self.client._delete_request(url_path, headers=header)
        mock_request.assert_called_with('delete', url_path, audit=False, headers=header)

    # CATEGORIA
    # ---------------------------------------------------------------------
    @patch('faasclient.client.Client._get_request')
    def test_categoria_list(self, mock_request):

        self.client.categoria_list()
        mock_request.assert_called_once_with('/categorias')

    @patch('faasclient.client.Client._post_request')
    def test_categoria_create(self, mock_request):

        name = 'categoria'

        self.client.categoria_create(name)
        mock_request.assert_called_once_with('/categorias', {'name': name})

    @patch('faasclient.client.Client._put_request')
    def test_categoria_update(self, mock_request):

        id = 123
        name = 'nova categoria'

        self.client.categoria_update(id, name)
        mock_request.assert_called_once_with('/categorias/%d' % id, {
                                             'name': name
                                             })

    @patch('faasclient.client.Client._delete_request')
    def test_categoria_delete(self, mock_request):

        id = 123

        self.client.categoria_delete(id)
        mock_request.assert_called_once_with('/categorias/%d' % id)

    # FILER
    # ---------------------------------------------------------------------
    @patch('faasclient.client.Client._get_request')
    def test_export_get(self, mock_request):

        id = 123

        self.client.export_get(id)
        mock_request.assert_called_once_with('/exports/%d' % id)

    @patch('faasclient.client.Client._get_request')
    def test_export_list(self, mock_request):

        self.client.export_list()
        mock_request.assert_called_once_with('/exports')

    @patch('faasclient.client.Client._post_request')
    def test_export_create(self, mock_request):

        quota = 123456789
        categoria_id = 1

        self.client.export_create(quota, categoria_id)
        mock_request.assert_called_once_with('/exports', {
            'categoria': categoria_id, 'quota': quota, 'resource_id': None}, audit=False)

    @patch('faasclient.client.Client._post_request')
    def test_export_create_with_resource(self, mock_request):

        quota = 123456789
        categoria_id = 1
        resource_id = 'aaaa-bbbb-cccc'

        self.client.export_create(quota, categoria_id, resource_id)
        mock_request.assert_called_once_with('/exports', {
            'categoria': categoria_id, 'quota': quota, 'resource_id': 'aaaa-bbbb-cccc'}, audit=False)

    @patch('faasclient.client.Client._delete_request')
    def test_export_delete(self, mock_request):

        id = 123

        self.client.export_delete(id)
        mock_request.assert_called_once_with('/exports/%d' % id, audit=False)

    @patch('faasclient.client.Client._delete_request')
    def test_export_force_delete(self, mock_request):

        id = 123

        self.client.export_force_delete(id)
        mock_request.assert_called_once_with('/exports/%d/force' % id, audit=False)

    # FILER
    # ---------------------------------------------------------------------
    @patch('faasclient.client.Client._get_request')
    def test_filer_list(self, mock_request):

        self.client.filer_list()
        mock_request.assert_called_once_with('/filers')

    @patch('faasclient.client.Client._post_request')
    def test_filer_create(self, mock_request):

        vfiler = 'vbla'
        export_filer = 'bla'
        connection_filer = 'blabla'
        username = 'fake'
        password = 12345

        self.client.filer_create(vfiler, export_filer, connection_filer,
                                 username, password)
        mock_request.assert_called_with('/filers',
                                        {'vfiler': vfiler,
                                         'connection_filer': connection_filer,
                                         'export_filer': export_filer,
                                         'username': username,
                                         'password': password
                                         }
                                        )

    @patch('faasclient.client.Client._get_request')
    def test_filer_get(self, mock_request):

        id = 123

        self.client.filer_get(id)
        mock_request.assert_called_once_with('/filers/%d' % id)

    @patch('faasclient.client.Client._delete_request')
    def test_filer_delete(self, mock_request):

        id = 123

        self.client.filer_delete(id)
        mock_request.assert_called_once_with('/filers/%d' % id)

    @patch('faasclient.client.Client._put_request')
    def test_filer_update(self, mock_request):

        fakeid = 123
        vfiler = 'vbla'
        export_filer = 'bla'
        connection_filer = 'blabla'
        username = 'fake'
        password = 12345

        self.client.filer_update(fakeid, vfiler, export_filer,
                                 connection_filer, username, password)
        mock_request.assert_called_with('/filers/%d' % fakeid, {
                                         'vfiler': vfiler,
                                         'connection_filer': connection_filer,
                                         'export_filer': export_filer,
                                         'username': username,
                                         'password': password
                                         }
                                        )

    # VOLUME
    # ---------------------------------------------------------------------
    @patch('faasclient.client.Client._get_request')
    def test_volume_list(self, mock_request):

        self.client.volume_list()
        mock_request.assert_called_once_with('/volumes')

    @patch('faasclient.client.Client._post_request')
    def test_volume_create(self, mock_request):

        path = '/some/path'
        filer_id = 1
        categoria_id = 1
        maxsnapshots = 10

        self.client.volume_create(path, filer_id, categoria_id, maxsnapshots)
        mock_request.assert_called_once_with('/volumes', {
                                             'path': path,
                                             'filer_id': filer_id,
                                             'categoria_id': categoria_id,
                                             'maxsnapshots': maxsnapshots
                                             })

    @patch('faasclient.client.Client._get_request')
    def test_volume_get(self, mock_request):

        fakeid = 123

        self.client.volume_get(fakeid)
        mock_request.assert_called_once_with('/volumes/%d' % fakeid)

    @patch('faasclient.client.Client._delete_request')
    def test_volume_delete(self, mock_request):

        fakeid = 123

        self.client.volume_delete(fakeid)
        mock_request.assert_called_once_with('/volumes/%d' % fakeid)

    @patch('faasclient.client.Client._put_request')
    def test_volume_update(self, mock_request):

        fakeid = 123
        path = '/some/path'
        filer_id = 1
        categoria_id = 1
        maxsnapshots = 10

        self.client.volume_update(fakeid, path, filer_id, categoria_id,
                                  maxsnapshots)
        mock_request.assert_called_once_with('/volumes/%d' % fakeid, {
                                             'path': path,
                                             'filer_id': filer_id,
                                             'categoria_id': categoria_id,
                                             'maxsnapshots': maxsnapshots
                                             })

    @patch('faasclient.client.Client._get_request')
    def test_volumes_info(self, mock_request):

        self.client.volumes_info()
        mock_request.assert_called_once_with('/volumes-info')

    @patch('faasclient.client.Client._post_request')
    def test_volumes_update_info(self, mock_request):

        self.client.volumes_update_info()
        mock_request.assert_called_once_with('/volumes-info-update')

    # PERMISSAO
    # ---------------------------------------------------------------------
    @patch('faasclient.client.Client._get_request')
    def test_permission_list(self, mock_request):

        self.client.permission_list()
        mock_request.assert_called_once_with('/permissions')

    @patch('faasclient.client.Client._post_request')
    def test_permission_create(self, mock_request):

        name = 'permissao'

        self.client.permission_create(name)
        mock_request.assert_called_once_with('/permissions', {'name': name})

    @patch('faasclient.client.Client._get_request')
    def test_permission_get(self, mock_request):

        id = 123

        self.client.permission_get(id)
        mock_request.assert_called_once_with('/permissions/%d' % id)

    @patch('faasclient.client.Client._put_request')
    def test_permission_update(self, mock_request):

        id = 123
        name = 'permissao'

        self.client.permission_update(id, name)
        mock_request.assert_called_once_with('/permissions/%d' % id, {
                                             'name': name
                                             })

    @patch('faasclient.client.Client._delete_request')
    def test_permission_delete(self, mock_request):

        id = 123

        self.client.permission_delete(id)
        mock_request.assert_called_once_with('/permissions/%d' % id)

    # QUOTA
    # ---------------------------------------------------------------------
    @patch('faasclient.client.Client._get_request')
    def test_quota_get(self, mock_request):

        id = 123

        self.client.quota_get(id)
        mock_request.assert_called_once_with('/exports/%d/quota' % id)

    @patch('faasclient.client.Client._put_request')
    def test_quota_set(self, mock_request):

        id = 123
        quota = 123456789

        self.client.export_update(id, quota)
        mock_request.assert_called_once_with('/exports/%d' % id, {
                                             'quota': quota
                                             }, audit=False)

    @patch('faasclient.client.Client._delete_request')
    def test_quota_delete(self, mock_request):

        id = 123

        self.client.quota_delete(id)
        mock_request.assert_called_once_with('/exports/%d/quota' % id)

    # AUDIT
    # ---------------------------------------------------------------------
    @patch('faasclient.client.Client._get_request')
    def test_audit_list(self, mock_request):

        self.client.audit_list()
        mock_request.assert_called_once_with('/audits')

    @patch('faasclient.client.Client._get_request')
    def test_audit_get(self, mock_request):

        id = 123

        self.client.audit_get(id)
        mock_request.assert_called_once_with('/audits/%d' % id)

    @patch('faasclient.client.Client._get_request')
    def test_audit_export_get(self, mock_request):

        export_id = 123

        self.client.audit_export_get(export_id)
        mock_request.assert_called_once_with('/audits/export/%d' % export_id)

    # APPHOST
    # ---------------------------------------------------------------------
    @patch('faasclient.client.Client._get_request')
    def test_apphost_list(self, mock_request):

        self.client.apphost_list()
        mock_request.assert_called_once_with('/apphosts')

    @patch('faasclient.client.Client._post_request')
    def test_apphost_create(self, mock_request):

        ip = '1.1.1.1'
        hostname = 'my-hostname'

        self.client.apphost_create(ip, hostname)
        mock_request.assert_called_once_with('/apphosts', {
                                             'ip': ip,
                                             'hostname': hostname})

    @patch('faasclient.client.Client._get_request')
    def test_apphost_get(self, mock_request):

        id = 123
        self.client.apphost_get(id)
        mock_request.assert_called_once_with('/apphosts/%d' % id)

    @patch('faasclient.client.Client._put_request')
    def test_apphost_update(self, mock_request):

        id = 123
        ip = '2.2.2.2'
        hostname = 'my-hostname2'

        self.client.apphost_update(id, ip, hostname)
        mock_request.assert_called_once_with('/apphosts/%d' % id, {
                                             'ip': ip,
                                             'hostname': hostname})

    @patch('faasclient.client.Client._delete_request')
    def test_apphost_delete(self, mock_request):

        id = 123
        self.client.apphost_delete(id)
        mock_request.assert_called_once_with('/apphosts/%d' % id)

    # RESTORE / JOBS
    # ---------------------------------------------------------------------
    @patch('faasclient.client.Client._get_request')
    def test_jobs_restore_list(self, mock_request):
        self.client.jobs_list()
        mock_request.assert_called_once_with('/restore/jobs')

    @patch('faasclient.client.Client._get_request')
    def test_job_restore_get(self, mock_request):
        id = 123

        self.client.jobs_get(id)
        mock_request.assert_called_once_with('/restore/jobs/%d' % id)

    @patch('faasclient.client.Client._post_request')
    def test_restore_snapshot(self, mock_request):
        export_id = 123
        snapshot_id = 123

        self.client.snapshot_restore(export_id, snapshot_id)
        mock_request.assert_called_once_with('/exports/%d/snapshots/%d/restore' % (export_id, snapshot_id), audit=False)


    # ACCESS
    # ---------------------------------------------------------------------
    @patch('faasclient.client.Client._get_request')
    def test_access_list(self, mock_request):
        export_id_or_path = 123

        self.client.access_list(export_id_or_path)
        mock_request.assert_called_once_with('/exports/%d/hosts' % export_id_or_path)

    @patch('faasclient.client.Client._post_request')
    def test_access_create(self, mock_request):

        export_id_or_path = 123
        permission = 'read-write'
        host = '127.0.0.1'

        parameters = {'host': '127.0.0.1', 'permission': 'read-write'}

        self.client.access_create(export_id_or_path, permission, host)
        mock_request.assert_called_once_with('/exports/%d/hosts' % export_id_or_path, parameters, audit=False)

    @patch('faasclient.client.Client._get_request')
    def test_access_get(self, mock_request):

        export_id_or_path = 1
        access_id = 1

        self.client.access_get(export_id_or_path, access_id)
        mock_request.assert_called_once_with('/exports/%d/hosts/%d' % (export_id_or_path, access_id))

    @patch('faasclient.client.Client._delete_request')
    def test_access_delete(self, mock_request):

        export_id_or_path = 1
        access_id = 2

        self.client.access_delete(export_id_or_path, access_id)
        mock_request.assert_called_once_with('/exports/%d/hosts/%d' % (export_id_or_path, access_id), audit=False)

    # SNAPSHOT
    # ---------------------------------------------------------------------
    @patch('faasclient.client.Client._get_request')
    def snapshot_list(self, mock_request):
        export_id_or_path = 123

        self.client.snapshot_list(export_id_or_path)
        mock_request.assert_called_once_with('/exports/%d/snapshots' % export_id_or_path)

    @patch('faasclient.client.Client._post_request')
    def test_snapshot_create(self, mock_request):

        export_id_or_path = 123

        self.client.snapshot_create(export_id_or_path)
        mock_request.assert_called_once_with('/exports/%d/snapshots' % export_id_or_path, audit=False)

    @patch('faasclient.client.Client._get_request')
    def test_snapshot_get(self, mock_request):

        export_id_or_path = 1
        snapshot_id = 2

        self.client.snapshot_get(export_id_or_path, snapshot_id)
        mock_request.assert_called_once_with('/exports/%d/snapshots/%d' % (export_id_or_path, snapshot_id))

    @patch('faasclient.client.Client._delete_request')
    def test_snapshot_delete(self, mock_request):

        export_id_or_path = 1
        snapshot_id = 2

        self.client.snapshot_delete(export_id_or_path, snapshot_id)
        mock_request.assert_called_once_with('/exports/%d/snapshots/%d' % (export_id_or_path, snapshot_id), audit=False)
