# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
from hashlib import sha256

# local imports
from appconf_node.users.models import User
from appconf_node.jwtlib import Jwt, NotAuthorizedError


class JwtAuthHandler(Jwt):
    def user_payload(self, user):
        if user is None:
            raise NotAuthorizedError()

        return {
            'identity': user.id,
            'secret': sha256(user.pw_hash.encode('utf-8')).hexdigest(),
        }

    def user_from_payload(self, payload):
        try:
            user_id = payload['identity']
            secret = payload['secret']

            user = User.query.get(user_id)

            if self._verify_user(user, secret):
                return user

        except KeyError:
            pass

        return None

    @staticmethod
    def _verify_user(user, secret):
        if user is None:
            return False

        return sha256(user.pw_hash.encode('utf-8')).hexdigest() == secret


jwt = JwtAuthHandler()
