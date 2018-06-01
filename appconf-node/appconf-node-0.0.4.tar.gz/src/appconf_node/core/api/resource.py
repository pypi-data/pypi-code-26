# -*- coding: utf-8 -*-
"""
Base class for resources using Google AppEngine ndb as storage.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from logging import getLogger

# 3rd party imports
from jsonschema import validate, ValidationError
from restible import RestResource
from serafin import Fieldspec, serialize
from six import iteritems

# local imports
from appconf_node.app import db


L = getLogger(__name__)


class SqlAlchemyResource(RestResource):
    """ Base class for ndb based resources.

    This provides a basic implementation that can be used out of the box. It
    provides no authentication/authorization.
    """
    name = None
    model = None
    spec = Fieldspec('*')
    schema = {}
    read_only = []

    def create_instance(self, values):
        item = self.model(**values)
        db.session.add(item)
        db.session.commit()

        return item

    def rest_query(self, request, params):
        """ Query existing records as a list. """
        fields = params.pop('_fields', '*')

        filters = self.deserialize(params)
        items = self.dbquery(filters).all()

        spec = Fieldspec(self.spec).restrict(Fieldspec(fields))
        ret = serialize(items, spec)
        return ret

    def rest_create(self, request, data):
        """ Create a new record. """
        try:
            validate(data, self.schema)

            values = self.deserialize(data)
            instance = self.create_instance(values)

            return serialize(instance, self.spec)

        except ValidationError as ex:
            return 400, {'detail': str(ex)}

    def rest_get(self, request, params):
        """ Get one record with the given id. """
        fields = params.get('_fields', '*')

        spec = Fieldspec(self.spec).restrict(Fieldspec(fields))
        item = self.get_requested(request)

        if item is not None:
            return serialize(item, spec)
        else:
            return 404, {'detail': "Not found"}

    def rest_update(self, request, data):
        schema = {}
        schema.update(self.schema)

        if 'required' in schema:
            del schema['required']

        try:
            validate(data, schema)

            item = self.get_requested(request)
            if item is None:
                return 404, {}

            values = self.deserialize(data)

            for name in self.read_only:
                values.pop(name, None)

            for name, value in iteritems(values):
                if name not in ('id',):
                    try:
                        setattr(item, name, value)
                    except AttributeError as ex:
                        L.exception("Failed to set attribute '{}'".format(name))
                        L.info(str(ex))
                        L.info("dir(ex):" + str(dir(ex)))

            db.session.commit()

            return 200, serialize(item, self.spec)
        except ValidationError as ex:
            return 400, {'detail': str(ex)}

    def rest_delete(self, request):
        """ DELETE detail. """
        item = self.get_requested(request)

        if item is None:
            return 404, {'detail': 'Item does not exist'}

        db.session.delete(item)
        db.session.commit()

        return 204, {}

    def deserialize(self, data):
        """ Convert JSON data into model field types.

        The value returned by this function can be used directly to create new
        instances and update existing ones.
        """
        return {n: self.get_field_value(n, v) for n, v in iteritems(data)}

    def get_field_value(self, name, value):
        """ Coerce value to a model field compatible representation. """
        return value

    def dbquery(self, filters):
        """ Return a model query with the given filters.

        The query can be further customised like any ndb query.

        :return google.appengine.ext.ndb.Query:
            The query with the given filters already applied.
        """
        filters = [getattr(self.model, n) == v for n, v in iteritems(filters)]
        return self.model.query.filter(*filters)

    def get_requested(self, request):
        pk = self.get_pk(request)
        return self.model.query.get(pk)
