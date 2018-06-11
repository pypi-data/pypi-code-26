# Copyright 2014 Oliver Cope
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

from functools import partial
import sys
from . import predicates

noop = lambda: None


def unauthenticated_response(environ, start_response):
    s = b"<html><body>Access is denied</body></html>"
    start_response("401 Unauthorized",
                   [("Content-Type", "text/html"),
                    ("Content-Length", str(len(s)))])
    return [s]


def unauthorized_response(environ, start_response):
    s = b"<html><body>Access is denied</body></html>"
    start_response("403 Forbidden",
                   [("Content-Type", "text/html"),
                    ("Content-Length", str(len(s)))])
    return [s]


def bind_exc_info(start_response):
    """
    Return a callable that forwards to ``start_response``, with exc_info baked
    in.
    """
    return partial(start_response, exc_info=sys.exc_info())


def KnaveMiddleware(app, acl, unauthorized_response=unauthorized_response):

    def knave_middleware(environ, start_response, acl_bind=acl.bind_to):
        acl_bind(environ)
        try:
            result = app(environ, start_response)
        except predicates.Unauthorized:
            if acl.is_authenticated():
                response = unauthorized_response
            else:
                response = unauthenticated_response
            for n in response(environ, bind_exc_info(start_response)):
                yield n
            return

        close = getattr(result, 'close', None)
        try:
            for n in result:
                yield n
        except predicates.Unauthorized:
            for n in unauthorized_response(environ, bind_exc_info(start_response)):
                yield n
        finally:
            if close is not None:
                close()

    return knave_middleware
