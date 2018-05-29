# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Import all routes so they can be easily imported with from routes import *
from .apps import *

# Static should be imported last as it contains a catch-all route
from .static import *
