# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from serafin import serialize

# local imports
from appconf_node.core.api import api_action
from appconf_node.core.api import Fieldspec
from appconf_node.core.api import SqlAlchemyResource
from .models import Site
from . import util


def enum_by_value(enum_cls, value):
    return next((x for x in enum_cls if x.value == value), None)


class SiteResource(SqlAlchemyResource):
    name = 'site'
    model = Site
    spec = Fieldspec('*,-ssl_key,-ssl_cert,-config_file')
    read_only = []

    def update_instance(self, instance, values):
        super(SiteResource, self).update_intance(instance, values)

        if instance.status == 'enabled':
            instance.start()        # This will write and reload nginx config

    @api_action()
    def start(self, obj, payload):
        try:
            obj.start()
        except RuntimeError as ex:
            return 400, {
                'site': serialize(obj),
                'detail': str(ex)
            }

        return 200, serialize(obj)

    @api_action()
    def stop(self, obj, payload):
        try:
            obj.stop()
        except RuntimeError as ex:
            return 400, {
                'site': serialize(obj),
                'detail': str(ex)
            }

        return 200, serialize(obj)

    @api_action()
    def config(self, obj, payload):
        return 200, obj.config

    @api_action(generic=True)
    def reload(self, payload):
        util.reload_nginx()

        return 200, {}
