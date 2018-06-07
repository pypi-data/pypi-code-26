#!/usr/bin/env python
# -*- coding: utf-8 -*-

from notmm.controllers.wsgi import WSGIController
from notmm.utils.django_settings import LazySettings
import logging
logger = logging.getLogger('notmm.controllers.wsgi')

_settings = LazySettings()

_default_manager = _settings.SCHEVO['connection_manager']

__all__ = ['ZODBController']

class ZODBController(WSGIController):

    key_prefix = 'schevo.db.'
    debug = True

    def __init__(self, request, db_name, manager=_default_manager, **kwargs):
        super(ZODBController, self).__init__(**kwargs)
        self.environ_key = self.key_prefix + 'zodb'
        self.setup_database(db_name)
        
    def setup_database(self, db_name):
        try:
            self.db = _default_manager[db_name]
        except KeyError:
            raise
        else:
            if not hasattr(self.db, db_name):
                self.db.db_name = db_name
            if self.debug:
                logger.debug("Configured database: %s" % self.db.db_name)

    def init_request(self, environ, force=True):
        request = super(ZODBController, self).init_request(environ)
        if self.debug:
            assert self.environ_key == 'schevo.db.zodb' # XXX use settings.SCHEVO['DATABASE_URL']

        if force:
            if not self.environ_key in request.environ:
                logger.debug("Setting schevo db in environ")
                request.environ[self.environ_key] = self.db
            else:
                logger.debug("Found db in environment: %s" % request.environ[self.environ_key])

        return request
