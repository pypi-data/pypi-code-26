"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from tornado import web

from pubkeeper.server.core.auth.local.models import User
from pubkeeper.server.core.auth.local.handlers import api_authenticated
from pubkeeper.server.core.auth.local.handlers.base import BaseHandler


class UserHandler(BaseHandler):

    @api_authenticated
    def get(self):
        with self._db as session:
            users = session.query(User).all()

        self.output_json(users)

    @api_authenticated
    def post(self):
        pass

    @api_authenticated
    def delete(self):
        if 'id' not in self.json_data:
            raise web.HTTPError(400, "User ID is required to delete")

        with self._db as session:
            user = session.query(User).filter_by(
                id=self.json_data['id']).first()

            if user is not None:
                session.delete(user)
                session.commit()
                self.set_status(204)
            else:
                raise web.HTTPError(404, "Unknown user id")
