# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: hydro_serving_grpc/tf/api/model.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='hydro_serving_grpc/tf/api/model.proto',
  package='hydrosphere.tensorflow.serving',
  syntax='proto3',
  serialized_pb=_b('\n%hydro_serving_grpc/tf/api/model.proto\x12\x1ehydrosphere.tensorflow.serving\x1a\x1egoogle/protobuf/wrappers.proto\"_\n\tModelSpec\x12\x0c\n\x04name\x18\x01 \x01(\t\x12,\n\x07version\x18\x02 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12\x16\n\x0esignature_name\x18\x03 \x01(\tB*\n%io.hydrosphere.serving.tensorflow.api\xf8\x01\x01\x62\x06proto3')
  ,
  dependencies=[google_dot_protobuf_dot_wrappers__pb2.DESCRIPTOR,])




_MODELSPEC = _descriptor.Descriptor(
  name='ModelSpec',
  full_name='hydrosphere.tensorflow.serving.ModelSpec',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='hydrosphere.tensorflow.serving.ModelSpec.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='version', full_name='hydrosphere.tensorflow.serving.ModelSpec.version', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='signature_name', full_name='hydrosphere.tensorflow.serving.ModelSpec.signature_name', index=2,
      number=3, type=9, cpp_type=9, label=1,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=105,
  serialized_end=200,
)

_MODELSPEC.fields_by_name['version'].message_type = google_dot_protobuf_dot_wrappers__pb2._INT64VALUE
DESCRIPTOR.message_types_by_name['ModelSpec'] = _MODELSPEC
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ModelSpec = _reflection.GeneratedProtocolMessageType('ModelSpec', (_message.Message,), dict(
  DESCRIPTOR = _MODELSPEC,
  __module__ = 'hydro_serving_grpc.tf.api.model_pb2'
  # @@protoc_insertion_point(class_scope:hydrosphere.tensorflow.serving.ModelSpec)
  ))
_sym_db.RegisterMessage(ModelSpec)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n%io.hydrosphere.serving.tensorflow.api\370\001\001'))
# @@protoc_insertion_point(module_scope)
