import grpc
from grpc import FutureTimeoutError

import capsule8.api.v0.subscription_pb2 as sub
import capsule8.api.v0.telemetry_service_pb2 as telem
import capsule8.api.v0.telemetry_service_pb2_grpc as telem_grpc

import capsule8.exceptions as cap8e


class SensorClient(object):
    def __init__(self, sensor="unix:/var/run/capsule8/sensor.sock", certs=None, connect=True):
        self.sensor = sensor
        self.certs = grpc.ssl_channel_credentials(
            open(certs).read()) if certs else None
        self.channel = self.create_channel() if connect else None
        self.subscription = {}

    @property
    def subscription(self):
        """
        grpc subscription to use when collecting telemetry
        """
        return self._subscription

    @subscription.setter
    def subscription(self, value):
        try:
            self._subscription = sub.Subscription(**value)
        except ValueError as e:
            raise cap8e.InvalidSubscriptionError(
                "Malformed subscription supplied: %s" % e)

    def create_channel(self, timeout=2):
        if self.certs:
            channel = grpc.secure_channel(self.sensor, self.certs)
        else:
            channel = grpc.insecure_channel(self.sensor)

        try:
            grpc.channel_ready_future(channel).result(timeout)
        except FutureTimeoutError:
            raise cap8e.SensorConnectionError(
                "Could not connect to sensor at %s. Is it running?" % self.sensor)
        return channel

    def get_telemetry_service(self):
        return telem_grpc.TelemetryServiceStub(self.channel)

    def subscribe(self, subscription):
        self.subscription = subscription

    def telemetry(self):
        service = self.get_telemetry_service()
        telemetry_stub_iterator = service.GetEvents(
            telem.GetEventsRequest(subscription=self.subscription))
        return telemetry_stub_iterator
