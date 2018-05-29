# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# local imports
from .app import db


class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    server_name = db.Column(db.String(500))
    status = db.Column(db.String(10))
    listen = db.Column(db.String(100), default='80')
    app_addr = db.Column(db.String(500))



