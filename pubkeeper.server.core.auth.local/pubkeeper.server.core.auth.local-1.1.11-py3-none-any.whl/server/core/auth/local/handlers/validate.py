"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
import json

from pubkeeper.server.core.auth.local.models import Token, Right
from pubkeeper.server.core.auth.local.handlers.base import BaseHandler


class ValidateHandler(BaseHandler):

    def post(self):
        with self._db as session:
            token = session.query(Token).filter_by(token=self.token,
                                                   revoked=False).first()
            if token:
                rights = session.query(Right).filter_by(token=self.token).all()
                self.write(json.dumps({'valid': True,
                                       'rights': [r.todict() for r in rights]}))
            else:
                self.write(json.dumps({'valid': False}))
