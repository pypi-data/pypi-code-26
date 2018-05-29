# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Import app as it is an interface for the whole package. Can be easily imported
# with from appconf.wsgi import app
from .app import app

# Import all routes
from .routes import *
