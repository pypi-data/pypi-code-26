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
import logging
from abc import abstractmethod, ABCMeta
from weakref import WeakValueDictionary

from rama.framework import InstanceId
from rama.utils.registry import TypeRegistry

LOG = logging.getLogger(__name__)


class Document(metaclass=ABCMeta):
    def __init__(self, file):
        self.file = file

    @abstractmethod
    def find_instances(self, element_class, context):
        pass


class InstanceRegistry:
    def __init__(self):
        self.id_instances = {}
        self.pk_instances = {}

    def set(self, instance_id, instance):
        if instance_id.keys is not None:
            if instance_id.is_column:
                for keys in instance_id.keys:
                    self.pk_instances[tuple(keys.tolist())] = instance
            else:
                self.pk_instances[tuple(instance_id.keys.tolist())] = instance
        self.id_instances[instance_id] = instance

    def get(self, instance_id):
        if not instance_id.is_column:
            return self.id_instances.get(instance_id, None)

        possible_instances = [self.pk_instances.get(tuple(keys.tolist()), None) for keys in instance_id.keys]
        if not any(possible_instances):
            return None
        return possible_instances


class Reader:
    def __init__(self, document: Document):
        self.instance_registry = InstanceRegistry()
        self.tables = {}
        self.column_mappings = {}
        self.registry = TypeRegistry.instance
        self.document = document

    @property
    def file(self):
        return self.document.file

    def get_type_by_id(self, type_id):
        return self.registry.get_by_id(type_id)

    def find_instances(self, cls):
        return self.document.find_instances(cls, context=self)

    def add_instance(self, instance):
        if instance.__vo_id__ is not None:
            self.instance_registry.set(instance.__vo_id__, instance)

    def get_instance_by_id(self, instance_id):
        return self.instance_registry.get(instance_id)

    def add_table(self, table_id, table):
        self.tables[table_id] = table

    def get_table_by_id(self, table_id):
        return self.tables.get(table_id, None)

    def add_column_mapping(self, old, new):
        self.column_mappings[old] = new

    def get_column_mapping(self, old):
        return self.column_mappings.get(old, old)
