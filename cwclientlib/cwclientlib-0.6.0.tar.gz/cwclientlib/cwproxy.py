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

"""A CWProxy class wraps a CubicWeb repository.

>>> import cwproxy
>>> p = cwproxy.CWProxy('https://www.cubicweb.org')
>>> a = p.rql('Any X,T WHERE X is Project, X title T')
>>> print(a.json())
"""

import json
import requests
import hmac
import hashlib
from datetime import datetime, date
import ssl

from six import text_type
from six.moves.urllib import parse as urlparse

if not getattr(ssl, 'HAS_SNI', False):
    try:
        import urllib3.contrib.pyopenssl
        urllib3.contrib.pyopenssl.inject_into_urllib3()
    except ImportError:
        pass

RQLIO_API = '1.0'


# useful to handle py2/py3 compat
def enc(s):
    if isinstance(s, text_type):
        return s.encode('utf-8')
    return s


class SignedRequestAuth(requests.auth.AuthBase):
    """Auth implementation for CubicWeb with cube signedrequest"""

    HEADERS_TO_SIGN = ('Content-MD5', 'Content-Type', 'Date')

    def __init__(self, token_id, secret):
        self.token_id = token_id
        self.secret = secret

    def __call__(self, req):
        content = ''
        if req.body:
            content = req.body
        req.headers['Content-MD5'] = hashlib.md5(enc(content)).hexdigest()
        content_to_sign = enc(req.method
                              + req.url
                              + ''.join(req.headers.get(field, '')
                                        for field in self.HEADERS_TO_SIGN))
        content_signed = hmac.new(enc(self.secret),
                                  content_to_sign).hexdigest()
        req.headers['Authorization'] = 'Cubicweb %s:%s' % (self.token_id,
                                                           content_signed)
        return req


def date_header_value():
    return datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')


class RemoteValidationError(Exception):
    pass


class CWProxy(object):
    """CWProxy: A simple helper class to ease building CubicWeb_
    clients. It allows to:

    * execute RQL_ queries remotely (using rqlcontroller_),
    * access instances that requires authentication (using signedrequest_).

.. _CubicWeb: http://www.cubicweb.org/
.. _RQL: http://docs.cubicweb.org/annexes/rql/language
.. _rqlcontroller: http://www.cubicweb.org/project/cubicweb-rqlcontroller/
.. _signedrequest: http://www.cubicweb.org/project/cubicweb-signedrequest/
    """

    def __init__(self, base_url, auth=None, verify=None, timeout=None):
        """Create a CWProxy connection object to the :base_url: cubicweb app.

        :param auth: can be provided to handle authentication. For a
          cubicweb application providing the signedrequest_ feature,
          one can use the SignedRequestAuth authentifier.

        :param verify: can be False to disable server certificate
          checking, or the path to a CA bundle file.

        """
        purl = urlparse.urlparse(base_url)
        # we do **not** want urls to be built with a double /, (e.g.
        # http://host// or http://host//basepath)
        path = purl.path.strip('/')
        if path:
            path = '{}/{}'.format(purl.netloc, path)
        else:
            path = purl.netloc
        self.base_url = (purl.scheme, path)
        self.auth = auth
        self.timeout = timeout
        self._ssl_verify = verify
        self._default_vid = 'jsonexport'  # OR 'ejsonexport'?
        self._base_url = urlparse.urlunparse(self.base_url +
                                             ('', None, None, None))

    def handle_request(self, method, path, **kwargs):
        """Construct a requests.Request and send it through this proxy.

        Arguments are that of requests.request() except for `path` which will
        be used to build a full URL using the base URL bound to this proxy.
        """
        msg = "handle_request() got unexpected keyword argument '{}'"
        for unexpected in ('url', 'auth'):
            if unexpected in kwargs:
                raise TypeError(msg.format(unexpected))
        url = self.build_url(path)
        kwargs['auth'] = self.auth
        kwargs.setdefault('headers', {}).update(
            {'Date': date_header_value()}
        )
        kwargs.setdefault('verify', self._ssl_verify)
        kwargs.setdefault('timeout', self.timeout)
        return requests.request(method, url, **kwargs)

    def build_url(self, path, query=None):
        """Build the URL to query from self.base_url and the given path

        :param path: can be a string or an iterable of strings; if it
            is a string, it can be a simple path, in which case the
            URL will be built from self.base_url + path, or it can be
            an "absolute URL", in which case it will be queried as is
            (the query argument is then ignored)

        :param query: can be a sequence of two-elements **tuples** or
            a dictionary (ignored if path is an absolute URL)

        """
        if query:
            query = urlparse.urlencode(query, doseq=True)
        if isinstance(path, (list, tuple)):
            path = '/'.join(path)
        if path.startswith(self._base_url):
            assert query is None
            return path
        return urlparse.urlunparse(self.base_url + (path, None, query, None))

    def get(self, path, query=None):
        """Perform a GET on the cubicweb instance

        :param path: the path part of the URL that will be GET
        :param query: can be a sequence of two-element tuples or a doctionnary
        """
        headers = {'Accept': 'application/json'}
        return self.handle_request('GET', path, params=query, headers=headers)

    def post(self, path, **data):
        """Perform a POST on the cubicweb instance

        :param path: the path part of the URL that will be GET
        :param **data: will be passed as the 'data' of the request
        """
        kwargs = {
            'headers': {'Accept': 'application/json'},
            'data': data,
        }
        if 'files' in data:
            kwargs['files'] = data.pop('files')
        return self.handle_request('POST', path, **kwargs)

    def post_json(self, path, payload):
        """Perform a POST on the cubicweb instance with application/json
        Content-Type.

        :param path: the path part of the URL that will be GET
        :param payload: native data to be sent as JSON (not encoded)
        """
        kwargs = {
            'headers': {'Accept': 'application/json'},
            'json': payload,
        }
        return self.handle_request('POST', path, **kwargs)

    def view(self, vid, **args):
        """Perform a GET on <base_url>/view with <vid> and <args>

        :param vid: the vid of the page to retrieve
        :param **args: will be used to build the query string of the URL
        """
        args['vid'] = vid
        return self.get('/view', args)

    def execute(self, rql, args=None):
        """CW connection's like execute method.

        :param rql: should be a unicode string or a plain ascii string
        :param args: are the optional parameters used in the query (dict)
        """
        return self.rqlio([(rql, args or {})]).json()[0]

    def rql(self, rql, path='view', **data):
        """Perform an urlencoded POST to /<path> with rql=<rql>

        :param rql: should be a unicode string or a plain ascii string
        (warning, no string formating is performed)
        :param path: the path part of the generated URL
        :param **data: the 'data' of the request
        """
        if rql.split()[0] in ('INSERT', 'SET', 'DELETE'):
            raise ValueError('You must use the rqlio() method to make '
                             'write RQL queries')

        if not data.get('vid'):
            data['vid'] = self._default_vid
        if path == 'view':
            data.setdefault('fallbackvid', '404')
        if rql:  # XXX may be empty?
            if not rql.lstrip().startswith('rql:'):
                # add the 'rql:' prefix to ensure given rql is considered has
                # plain RQL so CubicWeb won't attempt other interpretation
                # (e.g. eid, 2 or 3 word queries, plain text)
                rql = 'rql:' + rql
            data['rql'] = rql

        headers = {
            'Accept': 'application/json',
            'Date': date_header_value(),
        }
        params = {'url': self.build_url(path),
                  'headers': headers,
                  'verify': self._ssl_verify,
                  'auth': self.auth,
                  'data': data,
                  }
        return requests.post(**params)

    def rqlio(self, queries):
        """Multiple RQL for reading/writing data from/to a CW instance.

        :param queries: list of queries, each query being a couple (rql, args)

        Example::

          queries = [('INSERT CWUser U: U login %(login)s, U upassword %(pw)s',
                      {'login': 'babar', 'pw': 'cubicweb rulez & 42'}),
                     ('INSERT CWGroup G: G name %(name)s',
                      {'name': 'pachyderms'}),
                     ('SET U in_group G WHERE G eid %(g)s, U eid %(u)s',
                      {'u': '__r0', 'g': '__r1'}),
                     ('INSERT File F: F data %(content)s, F data_name %(fn)s',
                      {'content': BytesIO('some binary data'),
                       'fn': 'toto.bin'}),
                    ]
          self.rqlio(queries)

        """
        headers = {
            'Accept': 'application/json',
            'Date': date_header_value(),
        }
        files = self.preprocess_queries(queries)

        params = {'url': self.build_url(('rqlio', RQLIO_API)),
                  'headers': headers,
                  'verify': self._ssl_verify,
                  'auth': self.auth,
                  'files': files,
                  }
        posted = requests.post(**params)
        if posted.status_code == 500:
            try:
                cause = posted.json()
            except Exception as exc:
                raise RemoteValidationError('%s (%s)', exc, posted.text)
            else:
                if 'reason' in cause:
                    # was a RemoteCallFailed
                    raise RemoteValidationError(cause['reason'])
        return posted

    def preprocess_queries(self, queries):
        """Pre process queries arguments to replace binary content by
        files to be inserted in the multipart HTTP query

        :param queries: list of queries, each query being a couple (rql, args)

        Any value that have a read() method will be threated as
        'binary content'.

        In the RQL query, binary value are replaced by unique '__f<N>'
        references (the ref of the file object in the multipart HTTP
        request).
        """

        files = {}
        for query_idx, (rql, args) in enumerate(queries):
            if args is None:
                continue
            for arg_idx, (k, v) in enumerate(args.items()):
                if hasattr(v, 'read') and callable(v.read):
                    # file-like object
                    fid = args[k] = '__f%d-%d' % (query_idx, arg_idx)
                    files[fid] = v
                elif isinstance(v, (date, datetime)):
                    args[k] = v.isoformat()
        files['json'] = ('json', json.dumps(queries), 'application/json')
        return files
