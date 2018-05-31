#!/usr/bin/env python
# -*- coding: utf-8 -*-
import grpc

from ava_engine.ava.engine_api_pb2 import StatusRequest, InitializeRequest
from ava_engine.ava.engine_core_pb2 import FeatureArguments, BoundingBox

from ava_engine.ava.feeds_api_pb2 import \
    CreateFeedRequest, \
    DeleteFeedRequest, \
    GetFeedRequest, \
    ListFeedsRequest, \
    ConfigureFeedRequest
from ava_engine.ava.images_api_pb2 import GetImageRequest, SearchImagesRequest
from ava_engine.ava.feature_classification_pb2 import ClassifyRequest
from ava_engine.ava.feature_face_recognition_pb2 import \
    DetectFaceRequest, \
    AddFaceRequestImageItem, \
    AddFaceRequest, \
    RemoveFaceRequest, \
    ListFacesRequest

from ava_engine.ava.engine_core_pb2 import ImageItem
from ava_engine.ava.service_api_pb2_grpc import EngineApiDefStub, FeedsApiDefStub, \
    ClassificationApiDefStub, FaceRecognitionApiDefStub, ImagesApiDefStub


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


class _FaceRecognitionFeature:
    def __init__(self, channel):
        self._channel = channel
        self._stub = FaceRecognitionApiDefStub(self._channel)

    def detect(self, feed_id, images):
        return self._stub.Detect(DetectFaceRequest(feed_id=feed_id, images=images))  # mv DetectFacesRequest

    def add_face(self, face_id, face_name, face_images):
        images = []
        for image in face_images:
            images.append(AddFaceRequestImageItem(
                data=image['data'],
                bounding_box=BoundingBox(
                    x_min=image['bounding_box']['x_min'],
                    x_max=image['bounding_box']['x_max'],
                    y_min=image['bounding_box']['y_min'],
                    y_max=image['bounding_box']['y_max'],
                )
            ))
        return self._stub.AddFace(AddFaceRequest(id=face_id, name=face_name, images=images))

    def remove_face(self, face_id):
        return self._stub.RemoveFace(RemoveFaceRequest(id=face_id))

    def list_faces(self):
        return self._stub.ListFaces(ListFacesRequest())


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


class _Images:
    def __init__(self, channel):
        self._channel = channel
        self._stub = ImagesApiDefStub(self._channel)

    def get(self, image_id):
        return self._stub.GetImage(GetImageRequest(id=image_id))

    def search(self, options):
        req = SearchImagesRequest(
            before=options.get('before'),
            after=options.get('after'),
            feed_ids=options.get('feed_ids'),
            limit=options.get('limit'),
            offset=options.get('offset')
        )
        return self._stub.SearchImages(req)


class AvaEngineClient:
    def __init__(self, host='localhost', port=50051):
        self._host = host
        self._port = port

        self._channel = grpc.insecure_channel('{host}:{port}'.format(host=host, port=port))
        self._stub = EngineApiDefStub(self._channel)

        self.classification = _ClassificationFeature(self._channel)
        self.face_recognition = _FaceRecognitionFeature(self._channel)
        self.feeds = _Feeds(self._channel)
        self._images = _Images(self._channel)

    @property
    def images(self):
        return self._images

    def status(self):
        return self._stub.Status(StatusRequest())

    def initialize(self, configuration):
        features = _features_to_feature_arguments(configuration.get('features', {}))
        return self._stub.Initialize(InitializeRequest(features=features))
