# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# local imports
from appconf_node.core.api import Fieldspec, SqlAlchemyResource
from appconf_node.core.api import api_action
from .models import User
from .auth import jwt


class UserResource(SqlAlchemyResource):
    name = 'user'
    model = User
    spec = Fieldspec('*,-pw_hash')

    def create_instance(self, values):
        return User.create(**values)

    @api_action(generic=True, protected=False)
    def login(self, payload):
        username = payload.get('username', None)
        password = payload.get('password', None)

        if not all([username, password, len(payload) == 2]):
            return 401, {'detail': "Invalid credentials"}

        user = User.authenticate(username, password)
        if user is None:
            return 401, {'detail': "Invalid credentials"}

        return 200, {
            'jwt_token': jwt.generate_token(user).decode('utf-8')
        }
