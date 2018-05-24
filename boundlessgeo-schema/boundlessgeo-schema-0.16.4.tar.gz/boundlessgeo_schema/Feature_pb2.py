# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: boundlessgeo_schema/Feature.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='boundlessgeo_schema/Feature.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n!boundlessgeo_schema/Feature.proto\"\x89\x01\n\x07\x46\x65\x61ture\x12\x0b\n\x03\x66id\x18\x01 \x01(\t\x12,\n\nproperties\x18\x02 \x03(\x0b\x32\x18.Feature.PropertiesEntry\x12\x10\n\x08geometry\x18\x03 \x01(\x0c\x1a\x31\n\x0fPropertiesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"Y\n\tOperation\x12!\n\toperation\x18\x01 \x01(\x0e\x32\x0e.OperationType\x12\x0e\n\x06source\x18\x02 \x01(\t\x12\x19\n\x07\x66\x65\x61ture\x18\x03 \x01(\x0b\x32\x08.Feature*3\n\rOperationType\x12\n\n\x06INSERT\x10\x00\x12\n\n\x06UPDATE\x10\x01\x12\n\n\x06\x44\x45LETE\x10\x02\x42-\n\x17\x63om.boundlessgeo.schemaB\nFeaturePbfZ\x06schemab\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_OPERATIONTYPE = _descriptor.EnumDescriptor(
  name='OperationType',
  full_name='OperationType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='INSERT', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='UPDATE', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DELETE', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=268,
  serialized_end=319,
)
_sym_db.RegisterEnumDescriptor(_OPERATIONTYPE)

OperationType = enum_type_wrapper.EnumTypeWrapper(_OPERATIONTYPE)
INSERT = 0
UPDATE = 1
DELETE = 2



_FEATURE_PROPERTIESENTRY = _descriptor.Descriptor(
  name='PropertiesEntry',
  full_name='Feature.PropertiesEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='Feature.PropertiesEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='value', full_name='Feature.PropertiesEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=_descriptor._ParseOptions(descriptor_pb2.MessageOptions(), _b('8\001')),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=126,
  serialized_end=175,
)

_FEATURE = _descriptor.Descriptor(
  name='Feature',
  full_name='Feature',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='fid', full_name='Feature.fid', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='properties', full_name='Feature.properties', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='geometry', full_name='Feature.geometry', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_FEATURE_PROPERTIESENTRY, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=38,
  serialized_end=175,
)


_OPERATION = _descriptor.Descriptor(
  name='Operation',
  full_name='Operation',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='operation', full_name='Operation.operation', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='source', full_name='Operation.source', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='feature', full_name='Operation.feature', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=177,
  serialized_end=266,
)

_FEATURE_PROPERTIESENTRY.containing_type = _FEATURE
_FEATURE.fields_by_name['properties'].message_type = _FEATURE_PROPERTIESENTRY
_OPERATION.fields_by_name['operation'].enum_type = _OPERATIONTYPE
_OPERATION.fields_by_name['feature'].message_type = _FEATURE
DESCRIPTOR.message_types_by_name['Feature'] = _FEATURE
DESCRIPTOR.message_types_by_name['Operation'] = _OPERATION
DESCRIPTOR.enum_types_by_name['OperationType'] = _OPERATIONTYPE

Feature = _reflection.GeneratedProtocolMessageType('Feature', (_message.Message,), dict(

  PropertiesEntry = _reflection.GeneratedProtocolMessageType('PropertiesEntry', (_message.Message,), dict(
    DESCRIPTOR = _FEATURE_PROPERTIESENTRY,
    __module__ = 'boundlessgeo_schema.Feature_pb2'
    # @@protoc_insertion_point(class_scope:Feature.PropertiesEntry)
    ))
  ,
  DESCRIPTOR = _FEATURE,
  __module__ = 'boundlessgeo_schema.Feature_pb2'
  # @@protoc_insertion_point(class_scope:Feature)
  ))
_sym_db.RegisterMessage(Feature)
_sym_db.RegisterMessage(Feature.PropertiesEntry)

Operation = _reflection.GeneratedProtocolMessageType('Operation', (_message.Message,), dict(
  DESCRIPTOR = _OPERATION,
  __module__ = 'boundlessgeo_schema.Feature_pb2'
  # @@protoc_insertion_point(class_scope:Operation)
  ))
_sym_db.RegisterMessage(Operation)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\027com.boundlessgeo.schemaB\nFeaturePbfZ\006schema'))
_FEATURE_PROPERTIESENTRY.has_options = True
_FEATURE_PROPERTIESENTRY._options = _descriptor._ParseOptions(descriptor_pb2.MessageOptions(), _b('8\001'))
# @@protoc_insertion_point(module_scope)
