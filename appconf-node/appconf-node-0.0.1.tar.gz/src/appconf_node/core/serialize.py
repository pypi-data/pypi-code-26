# -*- coding: utf-8 -*-
"""
serafin integration.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from datetime import date, datetime

# 3rd party imports
from serafin import Fieldspec, serialize as serafin_serialize
from appconf_node.app import db


def iter_public_properties(obj, predicate=None):
    """ Iterate over public properties of an object.

    :param Any obj:
        The object we want to get the properties of.
    :param function predicate:
        Additional predicate to filter out properties we're interested in. This
        function will be called on every property of the object with the
        property name and value as it arguments. If it returns True, the
        property will be yielded by this generator.
    """
    predicate = predicate or (lambda n, v: True)
    obj_type = type(obj)
    for name in dir(obj):
        if name.startswith('_'):
            continue

        member = getattr(obj_type, name)
        if not isinstance(member, property):
            continue

        try:
            value = getattr(obj, name)
            if predicate(name, value):
                yield name, value
        except AttributeError:
            pass


def serialize_flask_model_fields(model, spec, ctx):
    ret = {}

    columns = model.__table__.columns.items();

    for name, column in columns:
        if name in spec:
            value = getattr(model, name)
            ret[name] = serafin_serialize.raw(value, spec[name], ctx)

    return ret

@serafin_serialize.type(db.Model)
def serialize_flask_model(obj, spec, ctx):
    """ serafin serializer for ndb models. """
    if spec is True or spec.empty():
        return {}

    data = serialize_flask_model_fields(obj, spec, ctx)

    props = list(iter_public_properties(obj, lambda n, v: n in spec))
    data.update({
        name: serafin_serialize.raw(value, spec[name], ctx)
        for name, value in props
    })

    return data


def serialize(*args, **kw):
    kw.setdefault('dumpval', dump_val)
    return serafin_serialize(*args, **kw)


def dump_val(name, value):
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%dT%H:%M:%S')
    elif isinstance(value, date):
        return value.strftime('%Y-%m-%d')
    else:
        return value
