# Copyright 2018 Smithsonian Astrophysical Observatory
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
# disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import inspect
import logging
from abc import ABCMeta
from pprint import pprint, pformat
from weakref import WeakKeyDictionary

import numpy
from astropy.table import Column
from astropy.units import Quantity

LOG = logging.getLogger(__name__)


class VodmlDescriptor:
    def __init__(self, vodml_id, min_occurs=0, max_occurs=1):
        self.vodml_id = vodml_id
        self.default = None
        self.min = min_occurs
        self.max = max_occurs
        self.name = None
        self.values = WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.values.get(instance, self.default)

    def __set__(self, instance, value):
        self.values[instance] = value
        if hasattr(value, "__parent__"):
            value.__parent__ = instance

    def __delete__(self, instance):
        del self.values[instance]

    def __set_name__(self, owner, name):
        self.name = name

    def select_return_value(self, values):
        max_occurs = self.max
        if max_occurs == 1 and len(values) == 1:
            return values[0]

        if max_occurs == 1 and not values:
            return None

        return values


class Composition(VodmlDescriptor):
    def get_index(self, instance, instance_index):
        """
        For each member of the composition call unroll and return a list of the resulting instances
        """
        values = self.values[instance]
        if values is None:
            return
        return [value.__class__._unroll(value, instance_index) for value in values]


class Attribute(VodmlDescriptor):
    def __set__(self, instance, value):
        VodmlDescriptor.__set__(self, instance, value)
        if hasattr(value, 'cardinality'):  # BaseTypes
            instance.cardinality = value.cardinality
        elif isinstance(value, Quantity) and not value.isscalar or isinstance(value, Column):
            instance.cardinality = len(value)

    def get_index(self, instance, instance_index):
        value = self.values[instance]
        if _is_basetype(value):
            return value.__class__._unroll(value, instance_index)
        if _is_string(value):
            return value
        if value is not None:
            return value[instance_index]


class Reference(VodmlDescriptor):
    def get_index(self, instance, instance_index):
        """
        References should just pass through, unless they are from a column.
        """
        reference_wrapper = self.values[instance]
        return reference_wrapper.get(instance_index)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.values.get(instance, self.default).get(None)

    def __set__(self, instance, value):
        if not isinstance(value, ReferenceWrapper):
            set_value = SingleReferenceWrapper(value)
        else:
            set_value = value
        self.values[instance] = set_value


class ReferenceWrapper(metaclass=ABCMeta):
    pass


class SingleReferenceWrapper(ReferenceWrapper):
    def __init__(self, referenced_instance):
        self.referenced_instance = referenced_instance

    def get(self, _):
        return self.referenced_instance


class RowReferenceWrapper(ReferenceWrapper):
    def __init__(self, referenced_list):
        self.referenced_list = referenced_list

    def get(self, instance_index):
        if instance_index is None:
            return self.referenced_list
        else:
            return self.referenced_list[instance_index]


class BaseType:
    vodml_id = None

    def __init__(self):
        self.__parent__ = None
        self.__count = 0

    def set_field(self, field_name, field_instance):
        setattr(self, field_name, field_instance)

    @property
    def cardinality(self):
        return self.__count

    @cardinality.setter
    def cardinality(self, value):
        self.__count = value

    def unroll(self):
        return [self.__class__._unroll(self, instance_index) for instance_index in range(self.cardinality)]

    @classmethod
    def find(cls, function, iterable):
        return list(filter(function, iterable))

    @classmethod
    def find_fields(cls):
        def is_field(attr):
            return inspect.isdatadescriptor(attr) and isinstance(attr, VodmlDescriptor)

        return inspect.getmembers(cls, is_field)

    @classmethod
    def _unroll(cls, template_instance, instance_index):
        instance = cls()
        for field_name, field_object in cls.find_fields():
            value = field_object.get_index(template_instance, instance_index)
            instance.set_field(field_name, value)
        return instance

    @classmethod
    def all_subclasses(cls):
        return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in c.all_subclasses()])

    def __repr__(self):
        original = numpy.get_printoptions()['threshold']
        numpy.set_printoptions(threshold=10)

        def what_to_display(value):
            if hasattr(value, '__vo_object__'):
                return {'adapter': value.__class__, 'object': value.__vo_object__}
            if isinstance(value, numpy.ndarray):
                return str(value)
            else:
                return value
        try:
            type_name = '.'.join((self.__class__.__module__, self.__class__.__name__))
            contents = [(p[0], getattr(self, p[0])) for p in self.find_fields()]
            contents = {elem[0]: what_to_display(elem[1]) for elem in contents}
            string = pformat({type_name: contents}, width=160)
        finally:
            numpy.set_printoptions(threshold=original)

        return string


class InstanceId:
    def __init__(self, id=None, keys=None):
        self.id = id
        self.keys = keys
        self.is_column = keys is not None and len(keys.shape) == 2

    def __repr__(self):
        return f"ID: {self.id} and Keys: {self.keys}"

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return numpy.array_equal(self.id, other.id) and numpy.array_equal(self.keys, other.keys)
        return False

    def __hash__(self):
        id_to_hash = self.id
        keys_to_hash = self.keys
        if hasattr(self.id, "tostring"):
            id_to_hash = self.id.tostring()
        if hasattr(self.keys, "tostring"):
            keys_to_hash = self.keys.tostring()

        return hash((id_to_hash, keys_to_hash))


def _is_string(value):
    return isinstance(value, str)


def _is_basetype(value):
    return isinstance(value, BaseType)