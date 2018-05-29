# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from passlib.hash import pbkdf2_sha512 as passlib

# local imports
from .app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    pw_hash = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True)

    def set_password(self, password):
        self.pw_hash = passlib.hash(password)

    @classmethod
    def create(cls, username, password, email):
        user = cls(name=username, email=email)

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter(User.name == username).scalar()

        if user is None:
            return

        return user if passlib.verify(password, user.pw_hash) else None
