# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import dialogflow_v2.proto.intent_pb2 as google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2
import google.longrunning.operations_pb2 as google_dot_longrunning_dot_operations__pb2
import google.protobuf.empty_pb2 as google_dot_protobuf_dot_empty__pb2


class IntentsStub(object):
  """Manages agent intents.


  Refer to the [Dialogflow documentation](https://dialogflow.com/docs/intents)
  for more details about agent intents.
  #
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.ListIntents = channel.unary_unary(
        '/google.cloud.dialogflow.v2.Intents/ListIntents',
        request_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.ListIntentsRequest.SerializeToString,
        response_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.ListIntentsResponse.FromString,
        )
    self.GetIntent = channel.unary_unary(
        '/google.cloud.dialogflow.v2.Intents/GetIntent',
        request_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.GetIntentRequest.SerializeToString,
        response_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.Intent.FromString,
        )
    self.CreateIntent = channel.unary_unary(
        '/google.cloud.dialogflow.v2.Intents/CreateIntent',
        request_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.CreateIntentRequest.SerializeToString,
        response_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.Intent.FromString,
        )
    self.UpdateIntent = channel.unary_unary(
        '/google.cloud.dialogflow.v2.Intents/UpdateIntent',
        request_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.UpdateIntentRequest.SerializeToString,
        response_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.Intent.FromString,
        )
    self.DeleteIntent = channel.unary_unary(
        '/google.cloud.dialogflow.v2.Intents/DeleteIntent',
        request_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.DeleteIntentRequest.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.BatchUpdateIntents = channel.unary_unary(
        '/google.cloud.dialogflow.v2.Intents/BatchUpdateIntents',
        request_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.BatchUpdateIntentsRequest.SerializeToString,
        response_deserializer=google_dot_longrunning_dot_operations__pb2.Operation.FromString,
        )
    self.BatchDeleteIntents = channel.unary_unary(
        '/google.cloud.dialogflow.v2.Intents/BatchDeleteIntents',
        request_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.BatchDeleteIntentsRequest.SerializeToString,
        response_deserializer=google_dot_longrunning_dot_operations__pb2.Operation.FromString,
        )


class IntentsServicer(object):
  """Manages agent intents.


  Refer to the [Dialogflow documentation](https://dialogflow.com/docs/intents)
  for more details about agent intents.
  #
  """

  def ListIntents(self, request, context):
    """Returns the list of all intents in the specified agent.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetIntent(self, request, context):
    """Retrieves the specified intent.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CreateIntent(self, request, context):
    """Creates an intent in the specified agent.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def UpdateIntent(self, request, context):
    """Updates the specified intent.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def DeleteIntent(self, request, context):
    """Deletes the specified intent.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def BatchUpdateIntents(self, request, context):
    """Updates/Creates multiple intents in the specified agent.

    Operation <response: [BatchUpdateIntentsResponse][google.cloud.dialogflow.v2.BatchUpdateIntentsResponse]>
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def BatchDeleteIntents(self, request, context):
    """Deletes intents in the specified agent.

    Operation <response: [google.protobuf.Empty][google.protobuf.Empty]>
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_IntentsServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'ListIntents': grpc.unary_unary_rpc_method_handler(
          servicer.ListIntents,
          request_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.ListIntentsRequest.FromString,
          response_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.ListIntentsResponse.SerializeToString,
      ),
      'GetIntent': grpc.unary_unary_rpc_method_handler(
          servicer.GetIntent,
          request_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.GetIntentRequest.FromString,
          response_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.Intent.SerializeToString,
      ),
      'CreateIntent': grpc.unary_unary_rpc_method_handler(
          servicer.CreateIntent,
          request_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.CreateIntentRequest.FromString,
          response_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.Intent.SerializeToString,
      ),
      'UpdateIntent': grpc.unary_unary_rpc_method_handler(
          servicer.UpdateIntent,
          request_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.UpdateIntentRequest.FromString,
          response_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.Intent.SerializeToString,
      ),
      'DeleteIntent': grpc.unary_unary_rpc_method_handler(
          servicer.DeleteIntent,
          request_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.DeleteIntentRequest.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'BatchUpdateIntents': grpc.unary_unary_rpc_method_handler(
          servicer.BatchUpdateIntents,
          request_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.BatchUpdateIntentsRequest.FromString,
          response_serializer=google_dot_longrunning_dot_operations__pb2.Operation.SerializeToString,
      ),
      'BatchDeleteIntents': grpc.unary_unary_rpc_method_handler(
          servicer.BatchDeleteIntents,
          request_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_intent__pb2.BatchDeleteIntentsRequest.FromString,
          response_serializer=google_dot_longrunning_dot_operations__pb2.Operation.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'google.cloud.dialogflow.v2.Intents', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
