# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# local imports
from appconf_node.core.api import Fieldspec, SqlAlchemyResource
from .models import Site, SiteProto, SiteStatus


def enum_by_value(enum_cls, value):
    return next((x for x in enum_cls if x.value == value), None)


class SiteResource(SqlAlchemyResource):
    name = 'site'
    model = Site
    spec = Fieldspec('*,-ssl_key,-ssl_cert,-config_path')
    read_only = []
