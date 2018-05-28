#!/usr/bin/env python
# -*- coding: utf-8 -*-
import grpc

from ava_engine.ava.engine_api_pb2 import StatusRequest, InitializeRequest
from ava_engine.ava.engine_core_pb2 import FeatureArguments
from ava_engine.ava.feeds_api_pb2 import CreateFeedRequest, DeleteFeedRequest, GetFeedRequest, ListFeedsRequest
from ava_engine.ava.feeds_api_pb2 import ConfigureFeedRequest
from ava_engine.ava.feature_classification_pb2 import ClassifyRequest

from ava_engine.ava.engine_core_pb2 import ImageItem
from ava_engine.ava.service_api_pb2_grpc import EngineApiDefStub, ClassificationApiDefStub, FeedsApiDefStub


def _features_to_feature_arguments(features):
    converted_features = {}
    for feature_type, feature_arguments in features.items():
        converted_features[feature_type] = FeatureArguments(
            classes=feature_arguments.get('classes', []),
            model_id=feature_arguments.get('model_id'),
            gpu_usage_fraction=feature_arguments.get('gpu_usage_fraction'),
        )
    return converted_features


class _ClassificationFeature:
    def __init__(self, channel):
        self._channel = channel
        self._stub = ClassificationApiDefStub(self._channel)

    def detect(self, feed_id, images, classes):
        return self._stub.Detect(ClassifyRequest(feed_id=feed_id, images=images, classes=classes))


class _Feeds:
    def __init__(self, channel):
        self._channel = channel
        self._stub = FeedsApiDefStub(self._channel)

    def create(self, feed_id):
        return self._stub.CreateFeed(CreateFeedRequest(id=feed_id))

    def delete(self, feed_id):
        return self._stub.DeleteFeed(DeleteFeedRequest(id=feed_id))

    def get(self, feed_id):
        return self._stub.GetFeed(GetFeedRequest(id=feed_id))

    def list(self):
        return self._stub.ListFeeds(ListFeedsRequest())

    def configure(self, feed_id, configuration):
        return self._stub.ConfigureFeed(ConfigureFeedRequest(
            id=feed_id,
            features=_features_to_feature_arguments(configuration.get('features', {})),
        ))


class AvaEngineClient:
    def __init__(self, host='localhost', port=50051):
        self._host = host
        self._port = port

        self._channel = grpc.insecure_channel('{host}:{port}'.format(host=host, port=port))
        self._stub = EngineApiDefStub(self._channel)

        self._features = {
            'classification': _ClassificationFeature(self._channel),
        }
        self._feeds = _Feeds(self._channel)

    @property
    def classification(self):
        return self._features['classification']

    @property
    def feeds(self):
        return self._feeds

    def status(self):
        return self._stub.Status(StatusRequest())

    def initialize(self, configuration):
        features = _features_to_feature_arguments(configuration.get('features', {}))
        return self._stub.Initialize(InitializeRequest(features=features))
