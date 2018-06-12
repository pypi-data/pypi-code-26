"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.server.core.auth.base import PubkeeperAuthModule
from pubkeeper.server.core.auth.local.db import Database
from pubkeeper.server.core.auth.local.handlers import \
    AuthLoginHandler, AuthLogoutHandler, TokenHandler, UserHandler, \
    ValidateHandler, WebHandler
from tornado import web
import os
import logging


class LocalAuthModule(PubkeeperAuthModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = logging.getLogger('pubkeeper.server.core.auth.local')

    def prepare(self, app, settings=None):
        database_conn_str = settings.get('database', None)
        if not database_conn_str:
            db_name = "pk_{}".format(
                settings.get('database_name', fallback='pk_auth')
            ).replace('-', '_')

            db_type = settings.get('database_type', fallback='postgresql')
            db_user = settings.get('database_user')
            db_pass = settings.get('database_pass')
            db_host = settings.get('database_host', fallback='localhost')
            db_port = settings.getint('database_port', fallback=5432)

            database_conn_str = "{}://{}:{}@{}:{}/{}".format(
                db_type, db_user, db_pass, db_host, db_port, db_name
            )
            self._logger.info("Connecting to db at {}://{}:{}/{}".format(
                db_type, db_host, db_port, db_name))

        routes = [
            (r"/auth/token",    TokenHandler),
            (r"/auth/validate", ValidateHandler),
            (r"/auth/user",     UserHandler),
            (r"/auth/login",    AuthLoginHandler),
            (r"/auth/logout",   AuthLogoutHandler),
        ]

        if settings.getboolean('enable_ui', fallback=False):
            path = os.path.dirname(os.path.realpath(__file__))
            routes += [
                (r"/", WebHandler),
                (r"/(favicon.ico)", web.StaticFileHandler, {
                    'path': "{}/site".format(path)
                }),
                (r"/static/(.*)", web.StaticFileHandler, {
                    'path': "{}/site/static".format(path)
                }),
                (r"/fonts/(.*)", web.StaticFileHandler, {
                    'path': "{}/site/fonts".format(path)
                })
            ]

        app.wildcard_router.add_rules(routes)
        app.db = Database(database_conn_str, settings)
        app.pk_settings = settings

        self._logger.info("Pubkeeper Server Authority: Prepared")

    def teardown(self):
        self._logger.info("Pubkeeper Server Authority: Shutdown")
