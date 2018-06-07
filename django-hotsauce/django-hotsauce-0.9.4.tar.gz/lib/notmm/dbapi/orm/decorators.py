#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2017 Etienne Robillard <tkadm30@yandex.com>
# All rights reserved.
"""Decorator functions to interact with Schevo databases"""

from functools import wraps
from notmm.controllers.zodb import ZODBController

__all__ = ('with_schevo_database',)


def with_schevo_database(dbname='db_default', controller_class=ZODBController):
    """
    Decorator that adds a Schevo database object reference
    in the ``request.environ`` dictionary.

    """


    def decorator(view_func, **kwargs):
        @wraps(view_func, **kwargs)
        def _wrapper(*args, **kwargs):
            req = args[0]
            wsgi_app = controller_class(req, dbname)
            req.environ[wsgi_app.environ_key] = wsgi_app.db
            return view_func(req, **kwargs)
        return wraps(view_func)(_wrapper, **kwargs)
        #return _wrapper
    return decorator

