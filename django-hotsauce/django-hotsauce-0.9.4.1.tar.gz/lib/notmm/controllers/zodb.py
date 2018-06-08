#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from notmm.controllers.wsgi import WSGIController


logger = logging.getLogger('notmm.controllers.wsgi')


__all__ = ['ZODBController']

class ZODBController(WSGIController):

    key_prefix = 'schevo.db.'
    debug = True

    def __init__(self, request, db_name, manager=None, **kwargs):
        super(ZODBController, self).__init__(**kwargs)
        self.environ_key = self.key_prefix + 'zodb'
        self.manager = manager
        self.setup_database(db_name)
        
    def setup_database(self, db_name):
        #print("DB NAME: %s" % db_name)
        try:
            if self.manager is not None:
                self.db = self.manager[db_name]
            else:
                from notmm.dbapi.orm import ClientStorageProxy
                self.db = ClientStorageProxy(db_name)
            if self.debug:
                assert self.db is not None
            self.db.db_name = db_name
        except (KeyError, AttributeError):
            raise
        else:
            if self.debug:
                logger.debug("Configured database: %s" % self.db.db_name)

    def init_request(self, environ):
        request = super(ZODBController, self).init_request(environ)
        if self.debug:
            assert self.environ_key == 'schevo.db.zodb' # XXX use settings.SCHEVO['DATABASE_URL']

        request.environ[self.environ_key] = self.db
        self._request = request # cheat!!!
        return request
