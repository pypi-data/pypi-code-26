from __future__ import absolute_import

from kafka.protocol.api import Request, Response
from kafka.protocol.types import Int16, Int32, Int64, String, Array, Schema, Bytes


class ProduceResponse_v0(Response):
    API_KEY = 0
    API_VERSION = 0
    SCHEMA = Schema(
        ('topics', Array(
            ('topic', String('utf-8')),
            ('partitions', Array(
                ('partition', Int32),
                ('error_code', Int16),
                ('offset', Int64)))))
    )


class ProduceResponse_v1(Response):
    API_KEY = 0
    API_VERSION = 1
    SCHEMA = Schema(
        ('topics', Array(
            ('topic', String('utf-8')),
            ('partitions', Array(
                ('partition', Int32),
                ('error_code', Int16),
                ('offset', Int64))))),
        ('throttle_time_ms', Int32)
    )


class ProduceResponse_v2(Response):
    API_KEY = 0
    API_VERSION = 2
    SCHEMA = Schema(
        ('topics', Array(
            ('topic', String('utf-8')),
            ('partitions', Array(
                ('partition', Int32),
                ('error_code', Int16),
                ('offset', Int64),
                ('timestamp', Int64))))),
        ('throttle_time_ms', Int32)
    )


class ProduceResponse_v3(Response):
    API_KEY = 0
    API_VERSION = 3
    SCHEMA = ProduceResponse_v2.SCHEMA


class ProduceResponse_v4(Response):
    """
    The version number is bumped up to indicate that the client supports KafkaStorageException.
    The KafkaStorageException will be translated to NotLeaderForPartitionException in the response if version <= 3
    """
    API_KEY = 0
    API_VERSION = 4
    SCHEMA = ProduceResponse_v3.SCHEMA


class ProduceResponse_v5(Response):
    API_KEY = 0
    API_VERSION = 5
    SCHEMA = Schema(
        ('topics', Array(
            ('topic', String('utf-8')),
            ('partitions', Array(
                ('partition', Int32),
                ('error_code', Int16),
                ('offset', Int64),
                ('timestamp', Int64),
                ('log_start_offset', Int64))))),
        ('throttle_time_ms', Int32)
    )


class ProduceRequest(Request):
    API_KEY = 0

    def expect_response(self):
        if self.required_acks == 0: # pylint: disable=no-member
            return False
        return True


class ProduceRequest_v0(ProduceRequest):
    API_VERSION = 0
    RESPONSE_TYPE = ProduceResponse_v0
    SCHEMA = Schema(
        ('required_acks', Int16),
        ('timeout', Int32),
        ('topics', Array(
            ('topic', String('utf-8')),
            ('partitions', Array(
                ('partition', Int32),
                ('messages', Bytes)))))
    )


class ProduceRequest_v1(ProduceRequest):
    API_VERSION = 1
    RESPONSE_TYPE = ProduceResponse_v1
    SCHEMA = ProduceRequest_v0.SCHEMA

class ProduceRequest_v2(ProduceRequest):
    API_VERSION = 2
    RESPONSE_TYPE = ProduceResponse_v2
    SCHEMA = ProduceRequest_v1.SCHEMA


class ProduceRequest_v3(ProduceRequest):
    API_VERSION = 3
    RESPONSE_TYPE = ProduceResponse_v3
    SCHEMA = Schema(
        ('transactional_id', String('utf-8')),
        ('required_acks', Int16),
        ('timeout', Int32),
        ('topics', Array(
            ('topic', String('utf-8')),
            ('partitions', Array(
                ('partition', Int32),
                ('messages', Bytes)))))
    )


class ProduceRequest_v4(ProduceRequest):
    """
    The version number is bumped up to indicate that the client supports KafkaStorageException.
    The KafkaStorageException will be translated to NotLeaderForPartitionException in the response if version <= 3
    """
    API_VERSION = 4
    RESPONSE_TYPE = ProduceResponse_v4
    SCHEMA = ProduceRequest_v3.SCHEMA


class ProduceRequest_v5(ProduceRequest):
    """
    Same as v4. The version number is bumped since the v5 response includes an additional
    partition level field: the log_start_offset.
    """
    API_VERSION = 5
    RESPONSE_TYPE = ProduceResponse_v5
    SCHEMA = ProduceRequest_v4.SCHEMA


ProduceRequest = [
    ProduceRequest_v0, ProduceRequest_v1, ProduceRequest_v2,
    ProduceRequest_v3, ProduceRequest_v4, ProduceRequest_v5
]
ProduceResponse = [
    ProduceResponse_v0, ProduceResponse_v1, ProduceResponse_v2,
    ProduceResponse_v3, ProduceResponse_v4, ProduceResponse_v5
]
