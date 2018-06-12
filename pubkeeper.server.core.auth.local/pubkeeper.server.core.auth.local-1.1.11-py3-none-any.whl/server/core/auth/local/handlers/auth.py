"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from tornado import web
from hashlib import sha256

from pubkeeper.server.core.auth.local.models import User
from pubkeeper.server.core.auth.local.handlers.base import BaseHandler


class AuthLoginHandler(BaseHandler):
    def post(self):
        if 'username' not in self.json_data:
            raise web.HTTPError(400, "Must provide username")

        if 'password' not in self.json_data:
            raise web.HTTPError(400, "Must provide password")

        with self._db as session:
            user = session.query(User).filter_by(
                username=self.json_data['username'],
                password=sha256(self.json_data['password'].encode()).hexdigest()
            ).first()

        if user:
            self.set_secure_cookie("pk_auth_user", str(user.id),
                                   expires_days=1)
        else:
            self.clear_cookie("pk_auth_user")
            raise web.HTTPError(401)


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("pk_auth_user")
