"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from tornado import web
from hashlib import sha256
from uuid import uuid4
from sqlalchemy.exc import IntegrityError
import json

from pubkeeper.server.core.auth.local.models import Token, Right
from pubkeeper.server.core.auth.local.handlers import api_authenticated
from pubkeeper.server.core.auth.local.handlers.base import BaseHandler


class TokenHandler(BaseHandler):
    @api_authenticated
    def get(self):
        with self._db as session:
            tokens = session.query(Token).all()

        self.output_json(tokens)

    def _token_exists(self):
        if not self.token:
            return False
        else:
            with self._db as session:
                return session.query(Token).filter_by(token=self.token).first()

    def _write_rights(self, reset=False):
        writable_rights = []

        for right in self.json_data['rights']:
            if 'topic' not in right:
                raise web.HTTPError(400, "Each right must define a "
                                         "topic for which it is valid")

            read = right['read'] if 'read' in right else 0
            write = right['write'] if 'write' in right else 0

            writable_rights.append(Right(token=self.token,
                                         topic=right['topic'],
                                         read=read,
                                         write=write))

        with self._db as session:
            if reset:
                session.query(Right).filter_by(token=self.token).delete()

            session.add_all(writable_rights)
            session.commit()

    @api_authenticated
    def post(self):
        if 'rights' not in self.json_data:
            raise web.HTTPError(400, "A set of rights for this token "
                                     "is required")

        if not self.token:
            self.token = sha256(uuid4().bytes).hexdigest()

        description = self.json_data['description'] or "No Description Given"

        try:
            token = Token(token=self.token, description=description)
            with self._db as session:
                session.add(token)
                session.commit()

            self._write_rights(True)
        except IntegrityError:
            raise web.HTTPError(409, "Token already exists") from None

        self.set_status(201)
        self.write(json.dumps({"token": self.token}))

    @api_authenticated
    def put(self):
        token = self._token_exists()
        if token is None:
            raise web.HTTPError(404, "A valid token is required to PUT")

        with self._db as session:
            session.delete(token)
            session.commit()
        self.post()
        self.set_status(200)

    @api_authenticated
    def patch(self):
        token = self._token_exists()
        if token is None:
            raise web.HTTPError(404, "A valid token is required to PATCH")

        try:
            if 'description' in self.json_data:
                token.description = self.json_data['description']

            if 'rights' in self.json_data:
                self._write_rights()

            self.set_status(200)
            self.write(json.dumps({"token": self.token}))
        except IntegrityError:
            raise web.HTTPError(409, "Unable to PATCH") from None

    @api_authenticated
    def delete(self):
        token = self._token_exists()
        if token is None:
            raise web.HTTPError(404, "A valid token is required to DELETE")

        with self._db as session:
            session.delete(token)
            session.commit()
