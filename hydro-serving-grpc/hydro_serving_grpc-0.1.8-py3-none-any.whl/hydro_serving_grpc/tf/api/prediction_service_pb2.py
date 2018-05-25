# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: hydro_serving_grpc/tf/api/prediction_service.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from hydro_serving_grpc.tf.api import predict_pb2 as hydro__serving__grpc_dot_tf_dot_api_dot_predict__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='hydro_serving_grpc/tf/api/prediction_service.proto',
  package='tensorflow.serving',
  syntax='proto3',
  serialized_pb=_b('\n2hydro_serving_grpc/tf/api/prediction_service.proto\x12\x12tensorflow.serving\x1a\'hydro_serving_grpc/tf/api/predict.proto2\x7f\n\x11PredictionService\x12j\n\x07Predict\x12..hydrosphere.tensorflow.serving.PredictRequest\x1a/.hydrosphere.tensorflow.serving.PredictResponseB\'\n%io.hydrosphere.serving.tensorflow.apib\x06proto3')
  ,
  dependencies=[hydro__serving__grpc_dot_tf_dot_api_dot_predict__pb2.DESCRIPTOR,])



_sym_db.RegisterFileDescriptor(DESCRIPTOR)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n%io.hydrosphere.serving.tensorflow.api'))

_PREDICTIONSERVICE = _descriptor.ServiceDescriptor(
  name='PredictionService',
  full_name='tensorflow.serving.PredictionService',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=115,
  serialized_end=242,
  methods=[
  _descriptor.MethodDescriptor(
    name='Predict',
    full_name='tensorflow.serving.PredictionService.Predict',
    index=0,
    containing_service=None,
    input_type=hydro__serving__grpc_dot_tf_dot_api_dot_predict__pb2._PREDICTREQUEST,
    output_type=hydro__serving__grpc_dot_tf_dot_api_dot_predict__pb2._PREDICTRESPONSE,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_PREDICTIONSERVICE)

DESCRIPTOR.services_by_name['PredictionService'] = _PREDICTIONSERVICE

# @@protoc_insertion_point(module_scope)
