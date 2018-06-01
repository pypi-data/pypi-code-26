# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
from enum import Enum

# 3rd party imports
from passlib.hash import pbkdf2_sha512 as passlib
from sqlalchemy_utils.types.choice import ChoiceType

# local imports
from appconf_node.app import db


class Role(Enum):
    admin = 'admin'
    client = 'client'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    pw_hash = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True)
    role = db.Column(ChoiceType(Role, impl=db.String(30)))

    @classmethod
    def create(cls, name, password, email, role=Role.client):
        user = cls(
            name=name,
            email=email,
            role=role
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user

    def set_password(self, password):
        self.pw_hash = passlib.hash(password)

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter(User.name == username).scalar()

        if user is None:
            return

        return user if passlib.verify(password, user.pw_hash) else None
