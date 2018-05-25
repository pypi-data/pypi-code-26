# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: onnx-operators_ONNX_NAMESPACE-ml.proto

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


import onnx_ONNX_NAMESPACE_ml_pb2 as onnx__ONNX__NAMESPACE__ml__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='onnx-operators_ONNX_NAMESPACE-ml.proto',
  package='ONNX_NAMESPACE',
  syntax='proto2',
  serialized_pb=_b('\n&onnx-operators_ONNX_NAMESPACE-ml.proto\x12\x0eONNX_NAMESPACE\x1a\x1connx_ONNX_NAMESPACE-ml.proto\"\xd3\x01\n\rFunctionProto\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x15\n\rsince_version\x18\x02 \x01(\x03\x12.\n\x06status\x18\x03 \x01(\x0e\x32\x1e.ONNX_NAMESPACE.OperatorStatus\x12\r\n\x05input\x18\x04 \x03(\t\x12\x0e\n\x06output\x18\x05 \x03(\t\x12\x11\n\tattribute\x18\x06 \x03(\t\x12\'\n\x04node\x18\x07 \x03(\x0b\x32\x19.ONNX_NAMESPACE.NodeProto\x12\x12\n\ndoc_string\x18\x08 \x01(\t\"{\n\rOperatorProto\x12\x0f\n\x07op_type\x18\x01 \x01(\t\x12\x15\n\rsince_version\x18\x02 \x01(\x03\x12.\n\x06status\x18\x03 \x01(\x0e\x32\x1e.ONNX_NAMESPACE.OperatorStatus\x12\x12\n\ndoc_string\x18\n \x01(\t\"\x8d\x02\n\x10OperatorSetProto\x12\r\n\x05magic\x18\x01 \x01(\t\x12\x12\n\nir_version\x18\x02 \x01(\x05\x12\x1d\n\x15ir_version_prerelease\x18\x03 \x01(\t\x12\x19\n\x11ir_build_metadata\x18\x07 \x01(\t\x12\x0e\n\x06\x64omain\x18\x04 \x01(\t\x12\x15\n\ropset_version\x18\x05 \x01(\x03\x12\x12\n\ndoc_string\x18\x06 \x01(\t\x12/\n\x08operator\x18\x08 \x03(\x0b\x32\x1d.ONNX_NAMESPACE.OperatorProto\x12\x30\n\tfunctions\x18\t \x03(\x0b\x32\x1d.ONNX_NAMESPACE.FunctionProto*.\n\x0eOperatorStatus\x12\x10\n\x0c\x45XPERIMENTAL\x10\x00\x12\n\n\x06STABLE\x10\x01')
  ,
  dependencies=[onnx__ONNX__NAMESPACE__ml__pb2.DESCRIPTOR,])

_OPERATORSTATUS = _descriptor.EnumDescriptor(
  name='OperatorStatus',
  full_name='ONNX_NAMESPACE.OperatorStatus',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='EXPERIMENTAL', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STABLE', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=699,
  serialized_end=745,
)
_sym_db.RegisterEnumDescriptor(_OPERATORSTATUS)

OperatorStatus = enum_type_wrapper.EnumTypeWrapper(_OPERATORSTATUS)
EXPERIMENTAL = 0
STABLE = 1



_FUNCTIONPROTO = _descriptor.Descriptor(
  name='FunctionProto',
  full_name='ONNX_NAMESPACE.FunctionProto',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='ONNX_NAMESPACE.FunctionProto.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='since_version', full_name='ONNX_NAMESPACE.FunctionProto.since_version', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='status', full_name='ONNX_NAMESPACE.FunctionProto.status', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='input', full_name='ONNX_NAMESPACE.FunctionProto.input', index=3,
      number=4, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='output', full_name='ONNX_NAMESPACE.FunctionProto.output', index=4,
      number=5, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='attribute', full_name='ONNX_NAMESPACE.FunctionProto.attribute', index=5,
      number=6, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='node', full_name='ONNX_NAMESPACE.FunctionProto.node', index=6,
      number=7, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='doc_string', full_name='ONNX_NAMESPACE.FunctionProto.doc_string', index=7,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=89,
  serialized_end=300,
)


_OPERATORPROTO = _descriptor.Descriptor(
  name='OperatorProto',
  full_name='ONNX_NAMESPACE.OperatorProto',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='op_type', full_name='ONNX_NAMESPACE.OperatorProto.op_type', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='since_version', full_name='ONNX_NAMESPACE.OperatorProto.since_version', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='status', full_name='ONNX_NAMESPACE.OperatorProto.status', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='doc_string', full_name='ONNX_NAMESPACE.OperatorProto.doc_string', index=3,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=302,
  serialized_end=425,
)


_OPERATORSETPROTO = _descriptor.Descriptor(
  name='OperatorSetProto',
  full_name='ONNX_NAMESPACE.OperatorSetProto',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='magic', full_name='ONNX_NAMESPACE.OperatorSetProto.magic', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ir_version', full_name='ONNX_NAMESPACE.OperatorSetProto.ir_version', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ir_version_prerelease', full_name='ONNX_NAMESPACE.OperatorSetProto.ir_version_prerelease', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ir_build_metadata', full_name='ONNX_NAMESPACE.OperatorSetProto.ir_build_metadata', index=3,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='domain', full_name='ONNX_NAMESPACE.OperatorSetProto.domain', index=4,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='opset_version', full_name='ONNX_NAMESPACE.OperatorSetProto.opset_version', index=5,
      number=5, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='doc_string', full_name='ONNX_NAMESPACE.OperatorSetProto.doc_string', index=6,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='operator', full_name='ONNX_NAMESPACE.OperatorSetProto.operator', index=7,
      number=8, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='functions', full_name='ONNX_NAMESPACE.OperatorSetProto.functions', index=8,
      number=9, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=428,
  serialized_end=697,
)

_FUNCTIONPROTO.fields_by_name['status'].enum_type = _OPERATORSTATUS
_FUNCTIONPROTO.fields_by_name['node'].message_type = onnx__ONNX__NAMESPACE__ml__pb2._NODEPROTO
_OPERATORPROTO.fields_by_name['status'].enum_type = _OPERATORSTATUS
_OPERATORSETPROTO.fields_by_name['operator'].message_type = _OPERATORPROTO
_OPERATORSETPROTO.fields_by_name['functions'].message_type = _FUNCTIONPROTO
DESCRIPTOR.message_types_by_name['FunctionProto'] = _FUNCTIONPROTO
DESCRIPTOR.message_types_by_name['OperatorProto'] = _OPERATORPROTO
DESCRIPTOR.message_types_by_name['OperatorSetProto'] = _OPERATORSETPROTO
DESCRIPTOR.enum_types_by_name['OperatorStatus'] = _OPERATORSTATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

FunctionProto = _reflection.GeneratedProtocolMessageType('FunctionProto', (_message.Message,), dict(
  DESCRIPTOR = _FUNCTIONPROTO,
  __module__ = 'onnx_operators_ONNX_NAMESPACE_ml_pb2'
  # @@protoc_insertion_point(class_scope:ONNX_NAMESPACE.FunctionProto)
  ))
_sym_db.RegisterMessage(FunctionProto)

OperatorProto = _reflection.GeneratedProtocolMessageType('OperatorProto', (_message.Message,), dict(
  DESCRIPTOR = _OPERATORPROTO,
  __module__ = 'onnx_operators_ONNX_NAMESPACE_ml_pb2'
  # @@protoc_insertion_point(class_scope:ONNX_NAMESPACE.OperatorProto)
  ))
_sym_db.RegisterMessage(OperatorProto)

OperatorSetProto = _reflection.GeneratedProtocolMessageType('OperatorSetProto', (_message.Message,), dict(
  DESCRIPTOR = _OPERATORSETPROTO,
  __module__ = 'onnx_operators_ONNX_NAMESPACE_ml_pb2'
  # @@protoc_insertion_point(class_scope:ONNX_NAMESPACE.OperatorSetProto)
  ))
_sym_db.RegisterMessage(OperatorSetProto)


# @@protoc_insertion_point(module_scope)
