# Copyright (C) 2018 Michał Góral.
#
# This file is part of TWWeb
#
# TWWeb is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TWWeb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TWWeb. If not, see <http://www.gnu.org/licenses/>.

from functools import wraps

from flask import make_response


def no_cache(view):
    @wraps(view)
    def _f(*a, **kw):
        resp = make_response(view(*a, **kw))
        resp.headers['Cache-Control'] = 'no-cache, no-store, max-age=0, \
                                        must-revalidate'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = 'Sat, 26 Jul 1997 01:00:00 GMT'
        return resp
    return _f
