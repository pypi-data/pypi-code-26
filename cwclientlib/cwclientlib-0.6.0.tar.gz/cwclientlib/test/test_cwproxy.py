# copyright 2014-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of cwclientlib.
#
# cwclientlib is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 2.1 of the License, or (at your
# option) any later version.
#
# cwclientlib is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with cwclientlib. If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO
import json
from datetime import date, datetime, timedelta

import pytz

import unittest

from cwclientlib.cwproxy import CWProxy, SignedRequestAuth

from cubicweb.devtools.httptest import CubicWebWsgiTC


class CWProxyClientTC(CubicWebWsgiTC):
    '''Basic tests for CWProxy'''
    def setup_database(self):
        with self.admin_access.client_cnx() as cnx:
            token = cnx.create_entity('AuthToken', id=u'testing',
                                      enabled=True,
                                      token_for_user=cnx.user.eid)
            self.admineid = cnx.user.eid
            self.token_id = token.id
            self.token_secret = token.token
            cnx.commit()

    @property
    def client(self):
        auth = SignedRequestAuth(token_id=self.token_id,
                                 secret=self.token_secret)
        base_url = self.config['base-url']
        return CWProxy(base_url=base_url, auth=auth)

    def test_rql(self):
        self.assertEqual([['admin'], ['anon']],
                         self.client.rql('Any L WHERE U login L').json())

        self.assertEqual([[self.admineid]],
                         self.client.rql('Any U WHERE U login "admin"').json())

    def test_execute(self):
        self.assertEqual([[self.admineid]],
                         self.client.execute('Any U WHERE U login %(l)s',
                                             {'l': 'admin'}))

    def test_rql_vid(self):
        admin = self.client.rql('Any U WHERE U login "admin"',
                                vid='ejsonexport').json()[0]
        self.assertIn('login', admin.keys())

    def test_rql_path(self):
        result = self.client.rql('Any U WHERE U login "admin"',
                                 path='test-controller').text
        self.assertEqual("coucou", result)

    def test_bad_rql_path(self):
        result = self.client.rql('CWGroup U WHERE U login "admin"')
        self.assertEqual(result.status_code, 500)

    def test_rqlio(self):
        queries = [('INSERT CWUser U: U login %(login)s, U upassword %(pw)s',
                    {'login': 'babar', 'pw': 'cubicweb rulez & 42'}),
                   ('INSERT CWGroup G: G name %(name)s',
                    {'name': 'pachyderms'}),
                   ('SET U in_group G WHERE G eid %(g)s, U eid %(u)s',
                    {'u': '__r0', 'g': '__r1'}),
                   ]

        results = self.client.rqlio(queries).json()
        self.assertEqual(3, len(results))
        babar = results[0][0][0]
        pach = results[1][0][0]

        with self.admin_access.client_cnx() as cnx:
            users = cnx.find('CWUser', eid=babar)
            self.assertEqual(1, len(users))
            self.assertEqual('babar', users.one().login)

            groups = cnx.find('CWGroup', eid=pach)
            self.assertEqual(1, len(groups))
            self.assertEqual('pachyderms', groups.one().name)

        self.assertEqual([babar, pach], results[2][0])

    def test_rqlio_no_kwargs(self):
        queries = [('INSERT CWUser U: U login "babar", '
                    'U upassword "cubicweb rulez & 42", '
                    'U in_group G WHERE G name "users"', None),
                   ]
        results = self.client.rqlio(queries).json()
        self.assertEqual(1, len(results))
        babar = results[0][0][0]
        with self.admin_access.client_cnx() as cnx:
            users = cnx.find('CWUser', eid=babar)
            self.assertEqual(1, len(users))
            self.assertEqual('babar', users.one().login)

    def test_rqlio_multiple_binary_arguments(self):
        queries = [
            ('INSERT User X: X name "babar",'
             ' X picture %(picture)s, X ssh_pubkey %(ssh_pubkey)s',
             {'picture': BytesIO(b'nice photo'),
              'ssh_pubkey': BytesIO(b'12345')}),
        ]

        eid = self.client.rqlio(queries).json()[0][0][0]
        with self.admin_access.client_cnx() as cnx:
            user = cnx.entity_from_eid(eid)
            self.assertEqual(user.picture.getvalue(), b'nice photo')
            self.assertEqual(user.ssh_pubkey.getvalue(), b'12345')

    def test_rqlio_datetime(self):
        md = datetime.now(pytz.timezone('Europe/Paris')) - timedelta(days=1)
        queries = [('INSERT CWUser U: U login "babar", '
                    'U creation_date %(cd)s, '
                    'U modification_date %(md)s, '
                    'U upassword "cubicweb rulez & 42", '
                    'U in_group G WHERE G name "users"', {'cd': md, 'md': md}),
                   ]

        eid = self.client.rqlio(queries).json()[0][0][0]
        with self.admin_access.client_cnx() as cnx:

            user = cnx.entity_from_eid(eid)
            self.assertEqual(md, user.creation_date)
            self.assertEqual(
                md.tzinfo.utcoffset(md),
                user.creation_date.tzinfo.utcoffset(user.creation_date))
            self.assertEqual(md, user.modification_date)

        # actually only check date type is handled, we can't expect a
        # given number of entities as it depends on the database cache
        # creation time
        res = self.client.execute('CWUser X WHERE X creation_date < %(today)s',
                                  {'today': date.today()})
        self.assertTrue(res)

    def test_handle_request(self):
        with self.admin_access.cnx() as cnx:
            eid = cnx.find('CWUser', login=u'admin')[0][0]
        response = self.client.handle_request(
            'GET', 'cwuser/{}'.format(eid),
            headers={'Accept': 'application/custom+json'},
        )
        # XXX getting 403 (as in test_get/test_view), don't know why.
        # self.assertEqual(response.status_code, 200)
        request = response.request
        self.assertEqual(request.method, 'GET')
        self.assertEqual(request.url,
                         '{}cwuser/{}'.format(self.config['base-url'], eid))
        headers = request.headers
        self.assertEqual(headers['Accept'], 'application/custom+json')
        self.assertIn('Date', headers)
        self.assertIn('Authorization', headers)
        self.assertIn('Content-MD5', headers)
        self.assertIn('Cubicweb testing:', headers['Authorization'])

    def test_handle_request_bad_parameter(self):
        with self.assertRaisesRegex(TypeError,
                                    "got unexpected keyword argument 'url'"):
            self.client.handle_request('GET', 1, url='x')

    @unittest.skip('to be completed and make pass')
    def test_get(self):
        with self.admin_access.client_cnx() as cnx:
            eid = cnx.find('CWEType', name=u'CWUser')[0][0]
        response = self.client.get('/cwetype/{}'.format(eid))
        self.assertEqual(response.status_code, 200)

    @unittest.skip('to be completed and make pass')
    def test_view(self):
        vid = 'jsonexport'
        with self.admin_access.web_request() as req:
            rset = req.find('CWEType', name=u'CWUser')
            json_view = req.view(vid, rset=rset)
        response = self.client.view(vid, eid=rset[0][0])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), json_view[0])

    def test_post(self):
        files = [('myfile', BytesIO(b'some content'))]
        data = dict(a='hello', files=files)
        response = self.client.post('/foo/bar', **data)
        self.assertEqual(response.status_code, 404)
        request = response.request
        self.assertEqual(request.method, 'POST')
        headers = request.headers
        content_type, _ = headers['Content-Type'].split('; ', 1)
        self.assertEqual(content_type, 'multipart/form-data')
        bodylines = request.body.splitlines()
        self.assertIn(b'Content-Disposition: form-data; name="a"', bodylines)
        self.assertIn(b'hello', bodylines)
        self.assertIn(
            b'Content-Disposition: form-data; name="myfile"; '
            b'filename="myfile"',
            bodylines,
        )
        self.assertIn(b'some content', bodylines)

    def test_post_json(self):
        data = {'foo': 1}
        response = self.client.post_json('/foo/bar', data)
        self.assertEqual(response.status_code, 404)
        request = response.request
        self.assertEqual(request.method, 'POST')
        headers = request.headers
        content_type = headers['Content-Type']
        self.assertEqual(content_type, 'application/json')
        body = request.body
        self.assertEqual(json.loads(body.decode('utf-8')), data)


class UtilsTests(unittest.TestCase):

    def test_base_url_slash_normalization(self):
        """test '/' can't appear twice in base_url

        e.g. we don't want ``http://www.logilab.org//``
        nor ``http://www.logilab.org//basepath``
        """
        proxy = CWProxy(base_url='http://www.logilab.org')
        self.assertEqual(proxy.base_url, ('http', 'www.logilab.org'))
        proxy = CWProxy(base_url='http://www.logilab.org/')
        self.assertEqual(proxy.base_url, ('http', 'www.logilab.org'))
        proxy = CWProxy(base_url='http://www.logilab.org/basepath')
        self.assertEqual(proxy.base_url, ('http', 'www.logilab.org/basepath'))
        proxy = CWProxy(base_url='http://www.logilab.org/basepath/')
        self.assertEqual(proxy.base_url, ('http', 'www.logilab.org/basepath'))

    def test_base_url_absolute_url(self):
        """test CWProxy.build_url parsing of absolute URLs
        """
        proxy = CWProxy(base_url='http://www.logilab.org')
        for url in ('http://www.logilab.org',
                    'http://www.logilab.org/path/to',
                    'http://www.logilab.org/path/to/',):
            self.assertEqual(url, proxy.build_url(url))

        proxy = CWProxy(base_url='http://www.logilab.org/with/path/')
        for url in ('http://www.logilab.org/with/path',
                    'http://www.logilab.org/with/path/to/something',
                    'http://www.logilab.org/with/path/to/something/',):
            self.assertEqual(url, proxy.build_url(url))


if __name__ == '__main__':
    from unittest import main
    main()
