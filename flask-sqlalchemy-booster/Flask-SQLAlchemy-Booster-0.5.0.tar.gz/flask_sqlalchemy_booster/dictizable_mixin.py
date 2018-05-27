"""DictizableMixin
A mixin class to add `todict` method to objects.

"""

from sqlalchemy.ext.associationproxy import AssociationProxy
from .utils import is_list_like, is_dict_like
from toolspy import deep_group
import json
from .json_encoder import json_encoder
from sqlalchemy.sql import sqltypes
from decimal import Decimal
from datetime import datetime, date
from .json_columns import JSONEncodedStruct
from toolspy import all_subclasses
from schemalite.core import func_and_desc
from sqlalchemy.orm import class_mapper
from types import NoneType


def serialized_list(olist, rels_to_expand=[]):
    return map(
        lambda o: o.todict(
            rels_to_expand=rels_to_expand),
        olist)


def _set_fields_for_col(col_name, col, schema, forbidden, required):
    if col_name not in forbidden:
        schema["fields"][col_name] = {
            "required": col_name in required,
            "allowed": col_name not in forbidden
        }
        if type(col.type) == JSONEncodedStruct:
            schema["fields"][col_name]["type"] = col.type.mutable_type
            if col.type.mutable_type == list and col.type.item_type is not None:
                schema["fields"][col_name]["list_item_type"] = col.type.item_type
        else:
            type_mapping = {
                sqltypes.Integer: (int, long),
                sqltypes.Numeric: (Decimal, float, int, long),
                sqltypes.DateTime: (datetime,),
                sqltypes.Date: (date,),
                sqltypes.Unicode: (unicode, str),
                sqltypes.UnicodeText: (unicode, str),
                sqltypes.String: (unicode, str),
                sqltypes.Text: (unicode, str),
                sqltypes.Boolean: (bool,),
                sqltypes.Enum: (unicode, str)
            }
            schema["fields"][col_name]["type"] = type_mapping[type(col.type)] + (NoneType, )


def _set_fields_for_rel(rel_name, rel, schema, forbidden, required):
    # if rel_name not in forbidden and rel.mapper.class_ not in seen_classes:
    if rel_name not in forbidden:
        schema["fields"][rel_name] = {
            "required": rel_name in required,
            "type": dict,
            "allowed": rel_name not in forbidden,
            "is_a_relation_to": rel.mapper.class_
        }
        if rel.uselist:
            schema["fields"][rel_name]["list_item_type"] = dict
            if rel.collection_class is None:
                schema["fields"][rel_name]["type"] = list
            else:
                schema["fields"][rel_name]["type"] = dict
                schema["fields"][rel_name]["is_mapped_collection"] = True
            # if show_rel_schema:
            #     schema["fields"][rel_name]["list_item_schema"] = rel.mapper.class_.generate_input_data_schema(
            #         seen_classes=seen_classes)
        # else:
        #     if show_rel_schema:
        #         schema["fields"][rel_name]["dict_schema"] = rel.mapper.class_.generate_input_data_schema(
        #             seen_classes=seen_classes)


class DictizableMixin(object):

    """Methods for converting Model instance to dict and json.

    Attributes:

        _attrs_to_serialize_ (list of str):  The columns which should
            be serialized as a part of the output dictionary

        _key_modifications_ (dict of str,str): A dictionary used to map
            the display names of columns whose original name we want
            to be modified in the json

        _rels_to_serialize_ (list of tuple of str):  A list of tuples. The
            first element of the tuple is the relationship
            that is to be serialized. The second element it the name of the
            attribute in the related model, the value of which is to be used
            as the representation

        _rels_to_expand_ (list of str): A list of relationships to expand.
            You can specify nested relationships by placing dots.

        _group_listrels_by_ (dict of str, list of str): A dictionary
            representing how to hierarchially group a list like relationship.
            The relationship fields are the keys and the list of the attributes
            based on which they are to be grouped are the values.


    """

    _attrs_to_serialize_ = []
    _attrs_forbidden_for_serialization_ = []
    _key_modifications_ = {}
    _rels_to_serialize_ = []
    _rels_to_expand_ = []
    _group_listrels_by_ = {}
    _autogenerate_dict_struct_if_none_ = False
    _dict_struct_ = None
    _input_data_schema_ = None

    @classmethod
    def input_schema_post_processor(cls, sch):
        return sch

    @classmethod
    def attrs_forbidden_for_serialization(cls):
        return cls._attrs_forbidden_for_serialization_

    @classmethod
    def attrs_for_autogenerated_dict_struct(cls):
        return class_mapper(cls).columns.keys() + cls.col_assoc_proxy_keys()



    def autogenerated_dict_structure(self):
        return {
            "attrs": self.attrs_for_autogenerated_dict_struct()
            # "attrs": class_mapper(type(self)).columns.keys() + type(self).col_assoc_proxy_keys()
        }

    @classmethod
    def input_data_schema(cls, required=None,
                          forbidden=None, post_processor=None):
        return cls._input_data_schema_ or cls.generate_input_data_schema(
            required=required, forbidden=forbidden,
            post_processor=post_processor)

    @classmethod
    def generate_input_data_schema(model_cls, required=None,
                                   forbidden=None, post_processor=None):
        # if seen_classes is None:
        #     seen_classes = []
        if required is None:
            required = []
        if forbidden is None:
            forbidden = []
        # seen_classes.append(model_cls)

        schema = {
            "fields": {
            }
        }

        def allowing_callable_for_polymorphic_classes(
                polymorphic_attr, polymorphic_identity):
            def _allowed(data, schema, context):
                return data.get(polymorphic_attr.key) == polymorphic_identity
            return _allowed

        cols_in_class = model_cls.__mapper__.columns.items()
        rels_in_class = model_cls.__mapper__.relationships.items()

        for col_name, col in cols_in_class:
            _set_fields_for_col(col_name, col, schema, forbidden, required)

        for rel_name, rel in rels_in_class:
            _set_fields_for_rel(
                rel_name, rel, schema, forbidden, required)
            # _set_fields_for_rel(
            #     rel_name, rel, schema, forbidden, required, seen_classes[0:])

        for assoc_proxy_name in model_cls.association_proxy_keys():
            schema['fields'][assoc_proxy_name] = {
                "allowed": True
            }

        polymorphic_attr = model_cls.__mapper__.polymorphic_on

        subclasses = filter(
            lambda sc: len(all_subclasses(sc)) == 0,
            all_subclasses(model_cls))

        if polymorphic_attr is not None:
            schema['fields'][polymorphic_attr.name] = {
                'allowed': True
            }
            if len(subclasses) == 0:
                del schema['fields'][polymorphic_attr.key]
            else:
                schema["polymorphic_on"] = polymorphic_attr.key
                schema["additional_schema_for_polymorphs"] = {
                }
                schema['fields'][polymorphic_attr.key]['permitted_values'] = [
                    sc.__mapper_args__['polymorphic_identity']
                    for sc in subclasses]

                for subcls in subclasses:
                    polymorphic_identity = subcls.__mapper_args__.get(
                        'polymorphic_identity')
                    schema["additional_schema_for_polymorphs"][
                        polymorphic_identity] = {"fields": {}}
                    cols_in_subcls = filter(
                        lambda col_item:
                        # col_item[1].table.name == subcls.__tablename__ and
                        # subcls.__tablename__ != model_cls.__tablename__ and
                        col_item[1].table.name != model_cls.__tablename__ and
                        not col_item[1].primary_key,
                        subcls.__mapper__.columns.items())
                    for col_name, col in cols_in_subcls:
                        _set_fields_for_col(
                            col_name, col,
                            schema["additional_schema_for_polymorphs"][
                                polymorphic_identity],
                            forbidden, required)
                    rels_in_subcls = filter(
                        lambda rel_item: not hasattr(model_cls, rel_item[0]),
                        subcls.__mapper__.relationships.items())
                    for rel_name, rel in rels_in_subcls:
                        _set_fields_for_rel(
                            rel_name, rel,
                            schema["additional_schema_for_polymorphs"][
                                polymorphic_identity],
                            forbidden, required)

                    for assoc_proxy_name in subcls.association_proxy_keys(
                            include_parent_classes=False):
                        schema["additional_schema_for_polymorphs"][
                            polymorphic_identity]['fields'][
                                assoc_proxy_name] = {"allowed": True}

        if post_processor and callable(post_processor):
            post_processor(schema)
        return schema

    @classmethod
    def pre_validation_adapter(cls, data, existing_instance=None):
        return data

    @classmethod
    def pre_validation_adapter_for_list(cls, data_list, existing_instances=None):
        if existing_instances is not None:
            return [cls.pre_validation_adapter(data, instance)
                    for data, instance in
                    zip(data_list, existing_instances)]
        else:
            return map(lambda data: cls.pre_validation_adapter(data), data_list)

    @classmethod
    def pre_validation_adapter_for_mapped_collection(cls, data_map, existing_instances=None):
        if existing_instances is not None:
            return {
                k: cls.pre_validation_adapter(v, existing_instances.get(k))
                for k, v in data_map.items()}
        else:
            return {k: cls.pre_validation_adapter(v) for k, v in data_map.items()}

    @classmethod
    def is_list_attribute(cls, rel):
        if rel in cls.__mapper__.relationships:
            return cls.__mapper__.relationships[rel].uselist
        rel_instance = getattr(cls, rel)
        if isinstance(rel_instance, AssociationProxy):
            return cls.__mapper__.relationships[
                rel_instance.target_collection].uselist
        return False

    @classmethod
    def max_permissible_dict_structure(cls):
        return {
            "attrs": cls.__mapper__.columns.keys(),
            "rels": {rel_name: {'attrs': rel_property.mapper.columns.keys()}
                     for rel_name, rel_property
                     in cls.__mapper__.relationships.items()}
        }

    @classmethod
    def output_data_schema(cls):
        return {
            "model_name": cls.__name__,
            "attrs": cls.__mapper__.columns.keys(),
            "rels": {
                rel_name: {
                    "rel_model_name": rel_property.mapper.class_.__name__,
                    "rel_type": "list" if rel_property.uselist else "scalar"
                }
                for rel_name, rel_property
                in cls.__mapper__.relationships.items()}
        }

    @classmethod
    def dict_structure(cls):
        if cls._dict_struct_ is None:
            return {
                "attrs": cls.__mapper__.columns.keys()
            }
        return cls._dict_struct_

    def to_serializable_dict(self, attrs_to_serialize=None,
                             rels_to_expand=None,
                             rels_to_serialize=None,
                             key_modifications=None):
        """
        An alias for `todict`
        """
        return self.todict(
            attrs_to_serialize=attrs_to_serialize,
            rels_to_expand=rels_to_expand, rels_to_serialize=rels_to_serialize,
            key_modifications=key_modifications)

    def todict_using_struct(self, dict_struct=None, dict_post_processors=None):
        """
            dict_struct:
            {
                'attrs': ['id', 'created_at'],
                'rels': {
                    'merchandise': {
                        'attrs': ['id', 'label']
                    }
                }
            }
        """
        # It is important to assign the passed kwarg to a differently named variable.
        # A dict is passed by reference and using the same kwarg here results in it
        # getting mutated - causing unforeseen side effects
        dict_struct_to_use = (
            self._dict_struct_ if dict_struct is None
            else dict_struct)
        if dict_struct_to_use is None and self._autogenerate_dict_struct_if_none_:
            dict_struct_to_use = self.autogenerated_dict_structure()
        elif dict_struct.get("attrs") is None:
            dict_struct_to_use = {}
            dict_struct_to_use["attrs"] = self.autogenerated_dict_structure()["attrs"]
            if "rels" in dict_struct:
                dict_struct_to_use["rels"] = dict_struct.get("rels")
        result = self.serialize_attrs(*dict_struct_to_use.get('attrs', []))
        for rel, rel_dict_struct in dict_struct_to_use.get('rels', {}).items():
            rel_obj = getattr(self, rel) if hasattr(self, rel) else None
            if rel_obj is not None:
                if is_list_like(rel_obj):
                    result[rel] = [i.todict_using_struct(dict_struct=rel_dict_struct)
                                   if hasattr(i, 'todict_using_struct') else i
                                   for i in rel_obj]
                elif is_dict_like(rel_obj):
                    result[rel] = {k: v.todict_using_struct(dict_struct=rel_dict_struct)
                                   if hasattr(v, 'todict_using_struct') else v
                                   for k, v in rel_obj.iteritems()}
                else:
                    result[rel] = rel_obj.todict_using_struct(
                        dict_struct=rel_dict_struct) if hasattr(
                        rel_obj, 'todict_using_struct') else rel_obj
            else:
                result[rel] = None
        if isinstance(dict_post_processors, list):
            for dict_post_processor in dict_post_processors:
                if callable(dict_post_processor):
                    result = dict_post_processor(result, self)
        return result


    # Version 5.0
    def todict(self, attrs_to_serialize=None,
               rels_to_expand=None,
               rels_to_serialize=None,
               group_listrels_by=None,
               key_modifications=None,
               dict_struct=None,
               dict_post_processors=None):

        """Converts an instance to a dictionary form

        Args:


            attrs_to_serialize (list of str):  The columns which should
                be serialized as a part of the output dictionary

            key_modifications (dict of str,str): A dictionary used to map
                the display names of columns whose original name we want
                to be modified in the json

            rels_to_serialize (list of tuple of str):  A list of tuples. The
                first element of the tuple is the relationship
                that is to be serialized. The second element it the name of the
                attribute in the related model, the value of which is to be used
                as the representation

            rels_to_expand (list of str): A list of relationships to expand.
                You can specify nested relationships by placing dots.

            group_listrels_by (dict of str, list of str): A dictionary
                representing how to hierarchially group a list like relationship.
                The relationship fields are the keys and the list of the attributes
                based on which they are to be grouped are the values.


        """

        # Never replace the following code by the (attrs = attrs or
        # self._attrs_) idiom. Python considers empty list as false. So
        # even if you pass an empty list, it will take self._x_ value. But
        # we don't want that as the empty list is what we use to end
        # the recursion
        dict_struct = (
            self._dict_struct_ if dict_struct is None
            else dict_struct)
        if dict_struct is None and self._autogenerate_dict_struct_if_none_:
            dict_struct = self.autogenerated_dict_structure()
        if dict_struct is not None:
            return self.todict_using_struct(
                dict_struct=dict_struct,
                dict_post_processors=dict_post_processors)
        attrs_to_serialize = (
            self._attrs_to_serialize_ if attrs_to_serialize is None
            else attrs_to_serialize)
        rels_to_serialize = (
            self._rels_to_serialize_ if rels_to_serialize is None
            else rels_to_serialize)
        rels_to_expand = (
            self._rels_to_expand_ if rels_to_expand is None
            else rels_to_expand)
        key_modifications = (
            self._key_modifications_ if key_modifications is None
            else key_modifications)
        group_listrels_by = (
            self._group_listrels_by_ if group_listrels_by is None
            else group_listrels_by)
        # Convert rels_to_expand to a dictionary
        rels_to_expand_dict = {}
        for rel in rels_to_expand:
            partitioned_rels = rel.partition('.')
            if partitioned_rels[0] not in rels_to_expand_dict:
                rels_to_expand_dict[partitioned_rels[0]] = (
                    [partitioned_rels[-1]] if partitioned_rels[-1]
                    else [])
            else:
                if partitioned_rels[-1]:
                    rels_to_expand_dict[partitioned_rels[0]].append(
                        partitioned_rels[-1])

        # # Convert grouplistrelsby to a dict
        # group_listrels_dict = {}
        # for rel_to_group, grouping_keys in group_listrels_by.iteritems():
        #     partitioned_rel_to_group = rel_to_group.partition('.')
        #     if partitioned_rel_to_group[0] not in group_listrels_dict:
        #         group_listrels_dict[partitioned_rel_to_group[0]] = (
        #             {partitioned_rel_to_group[-1]: grouping_keys}
        #             if partitioned_rel_to_group[-1] else grouping_keys)
        #     else:
        #         if partitioned_rel_to_group[-1]:
        #             group_listrels_dict[
        #                 partitioned_rel_to_group[0]][
        #                     partitioned_rel_to_group[-1]] = grouping_keys

        # Serialize attrs
        result = self.serialize_attrs(*attrs_to_serialize)

        # Serialize rels
        if len(rels_to_serialize) > 0:
            for rel, id_attr in rels_to_serialize:
                rel_obj = getattr(self, rel) if hasattr(self, rel) else None
                if rel_obj is not None:
                    if is_list_like(rel_obj):
                        if (group_listrels_by is not None and
                                rel in group_listrels_by):
                            result[rel] = deep_group(
                                rel_obj,
                                attr_to_show=id_attr,
                                keys=group_listrels_by[rel]
                            )
                        else:
                            result[rel] = [getattr(item, id_attr)
                                           for item in rel_obj if hasattr(item, id_attr)]
                    elif is_dict_like(rel_obj):
                        result[rel] = {k: getattr(v, id_attr)
                                       for k, v in rel_obj.iteritems()
                                       if hasattr(v, id_attr)}
                    else:
                        result[rel] = getattr(rel_obj, id_attr) if hasattr(
                            rel_obj, id_attr) else None
                else:
                    result[rel] = None

        # Expand some rels
        for rel, child_rels in rels_to_expand_dict.iteritems():
            rel_obj = getattr(self, rel) if hasattr(self, rel) else None
            if rel_obj is not None:
                if is_list_like(rel_obj):
                    if (group_listrels_by is not None and
                            rel in group_listrels_by):
                        result[rel] = deep_group(
                            rel_obj,
                            keys=group_listrels_by[rel], serializer='todict',
                            serializer_kwargs={'rels_to_expand': child_rels}
                        )
                    else:
                        result[rel] = [i.todict(rels_to_expand=child_rels)
                                       if hasattr(i, 'todict') else i
                                       for i in rel_obj]
                        # result[rel] = serialized_list(
                        #     rel_obj, rels_to_expand=child_rels)
                elif is_dict_like(rel_obj):
                    result[rel] = {k: v.todict()
                                   if hasattr(v, 'todict') else v
                                   for k, v in rel_obj.iteritems()}
                else:
                    result[rel] = rel_obj.todict(
                        rels_to_expand=child_rels) if hasattr(
                        rel_obj, 'todict') else rel_obj

        for key, mod_key in key_modifications.items():
            if key in result:
                result[mod_key] = result.pop(key)

        if isinstance(dict_post_processors, list):
            for dict_post_processor in dict_post_processors:
                if callable(dict_post_processor):
                    result = dict_post_processor(result, self)

        return result

    def serialize_attrs(self, *args):
        """Converts and instance to a dictionary with only the specified
        attributes as keys

        Args:
            *args (list): The attributes to serialize

        Examples:

            >>> customer = Customer.create(name="James Bond", email="007@mi.com",
                                           phone="007", city="London")
            >>> customer.serialize_attrs('name', 'email')
            {'name': u'James Bond', 'email': u'007@mi.com'}

        """
        # return dict([(a, getattr(self, a)) for a in args])
        cls = type(self)
        result = {}
        # result = {
        #     a: getattr(self, a)
        #     for a in args
        #     if hasattr(cls, a) and
        #     a not in cls.attrs_forbidden_for_serialization()
        # }
        for a in args:
            if hasattr(cls, a) and a not in cls.attrs_forbidden_for_serialization():
                val = getattr(self, a)
                if is_list_like(val):
                    result[a] = list(val)
                else:
                    result[a] = val
        return result
        # return dict([(a, getattr(self, a)) for a in args if hasattr(cls, a) and a not in cls.attrs_forbidden_for_serialization()])


    def tojson(self, attrs_to_serialize=None,
               rels_to_expand=None,
               rels_to_serialize=None,
               key_modifications=None):
        return json.dumps(
            self.todict(
                attrs_to_serialize=attrs_to_serialize,
                rels_to_expand=rels_to_expand,
                rels_to_serialize=rels_to_serialize,
                key_modifications=key_modifications),
            default=json_encoder)
