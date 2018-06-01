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

import datetime

from flask import current_app as app
from flask import Blueprint, request
from werkzeug import url_encode


filters = Blueprint('filters', __name__)


@filters.app_template_filter()
def strftime(val, fmt='%Y-%m-%d'):
    dt = datetime.datetime.strptime(val, '%Y%m%dT%H%M%SZ')
    return dt.strftime(fmt)

@filters.app_template_global()
def query(**kw):
    args = request.args.copy()
    multi_keys = app.config['TW_KEYS_HAS_CHECK']

    for key, val in kw.items():
        if key in multi_keys and key in args:
            if val not in args.get(key, '').split(','):
                args[key] += ',%s' % val
        else:
            args[key] = val
    return '%s?%s' % (request.path, url_encode(args))

@filters.app_template_global()
def has_query(**kw):
    return all(request.args.get(k) == v for k, v in kw.items())

@filters.app_template_global()
def eq_query(**kw):
    return request.args.to_dict() == kw

@filters.app_template_global()
def is_query():
    return bool(request.args)

@filters.app_template_global()
def query_values(*args):
    return [request.args[key] for key in args if key in request.args]

@filters.app_template_global()
def get_task(**kw):
    # TODO FIXME: Calling this in template is slooooow. Figure out other method
    # for getting task descriptions.
    return app.tw.get_task(**kw)[1]
