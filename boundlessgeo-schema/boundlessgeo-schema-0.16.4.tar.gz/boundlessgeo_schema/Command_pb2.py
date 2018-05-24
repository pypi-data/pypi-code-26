# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: boundlessgeo_schema/Command.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from boundlessgeo_schema import Metadata_pb2 as boundlessgeo__schema_dot_Metadata__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='boundlessgeo_schema/Command.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n!boundlessgeo_schema/Command.proto\x1a\"boundlessgeo_schema/Metadata.proto\"\xb5\x01\n\x07\x43ommand\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06\x61\x63tion\x18\x02 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\x0c\x12%\n\x07\x63ontext\x18\x04 \x01(\x0e\x32\x14.Command.ContextType\x12\x1b\n\x08metadata\x18\x05 \x01(\x0b\x32\t.Metadata\"<\n\x0b\x43ontextType\x12\x0b\n\x07\x44\x45SKTOP\x10\x00\x12\x07\n\x03WEB\x10\x01\x12\n\n\x06MOBILE\x10\x02\x12\x0b\n\x07SERVICE\x10\x03\x42-\n\x17\x63om.boundlessgeo.schemaB\nCommandPbfZ\x06schemab\x06proto3')
  ,
  dependencies=[boundlessgeo__schema_dot_Metadata__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_COMMAND_CONTEXTTYPE = _descriptor.EnumDescriptor(
  name='ContextType',
  full_name='Command.ContextType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='DESKTOP', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='WEB', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='MOBILE', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SERVICE', index=3, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=195,
  serialized_end=255,
)
_sym_db.RegisterEnumDescriptor(_COMMAND_CONTEXTTYPE)


_COMMAND = _descriptor.Descriptor(
  name='Command',
  full_name='Command',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Command.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='action', full_name='Command.action', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data', full_name='Command.data', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='context', full_name='Command.context', index=3,
      number=4, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='metadata', full_name='Command.metadata', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _COMMAND_CONTEXTTYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=74,
  serialized_end=255,
)

_COMMAND.fields_by_name['context'].enum_type = _COMMAND_CONTEXTTYPE
_COMMAND.fields_by_name['metadata'].message_type = boundlessgeo__schema_dot_Metadata__pb2._METADATA
_COMMAND_CONTEXTTYPE.containing_type = _COMMAND
DESCRIPTOR.message_types_by_name['Command'] = _COMMAND

Command = _reflection.GeneratedProtocolMessageType('Command', (_message.Message,), dict(
  DESCRIPTOR = _COMMAND,
  __module__ = 'boundlessgeo_schema.Command_pb2'
  # @@protoc_insertion_point(class_scope:Command)
  ))
_sym_db.RegisterMessage(Command)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\027com.boundlessgeo.schemaB\nCommandPbfZ\006schema'))
# @@protoc_insertion_point(module_scope)
