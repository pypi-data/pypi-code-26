# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# local imports
from appconf_node.core.api import Fieldspec, SqlAlchemyResource
from .models import User


class UserResource(SqlAlchemyResource):
    name = 'user'
    model = User
    spec = Fieldspec('*,-pw_hash')

    def create_instance(self, values):
        return User.create(**values)
