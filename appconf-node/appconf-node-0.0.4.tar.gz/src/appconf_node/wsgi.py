# -*- coding: utf-8 -*-
""" WSGI module to support 3rd party servers

Importing WSGI application from appconf_node.wsgi will also initialize it on
import. This won't happen if you import directly from appconf_node.app.
For example if you want to run gunicorn directly and bypass the provided
cli tool, you could do::

    gunicorn appconf_node.wsgi:application

The one below would not work, as ``app`` is None before calling ``init_app()``::

    gunicorn appconf_node.app:app

"""
from __future__ import absolute_import, unicode_literals

# local imports
from .app import init_app


application = init_app()
