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


import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect

import taskw

import twweb.views as views
from .jinja_filters import filters
from .model import db, login_manager
from .utils import make_db_uri


app = Flask(__name__)

try:
    app.config.from_object('twweb.config-dev')
except ImportError:
    pass

app.config.from_pyfile('twweb.cfg', silent=True)

# A default tuple of list-like (lists, comma-separated strings) taskwarrior's
# attributes which are searched by checking whether they contain a query (vs.
# being equal to the query)
app.config.setdefault('TW_KEYS_HAS_CHECK', ('tags', 'depends'))

app.config['SQLALCHEMY_DATABASE_URI'] = make_db_uri(app.config)

csrf = CSRFProtect(app)
db.init_app(app)
login_manager.init_app(app)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

twkw = dict(marshal=True)
taskrc = os.path.expanduser(app.config.get('TW_TASKRC', ''))
if os.path.isfile(taskrc):
    twkw['config_filename'] = taskrc

app.tw = taskw.TaskWarrior(**twkw)

app.register_blueprint(views.task_view)
app.register_blueprint(filters)


@app.before_first_request
def create_db():
    db.create_all()
