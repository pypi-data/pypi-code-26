from __future__ import absolute_import

from kafka.protocol.legacy import (
    create_message, create_gzip_message,
    create_snappy_message, create_message_set,
    CODEC_NONE, CODEC_GZIP, CODEC_SNAPPY, ALL_CODECS,
    ATTRIBUTE_CODEC_MASK, KafkaProtocol,
)

API_KEYS = {
    0: 'Produce',
    1: 'Fetch',
    2: 'ListOffsets',
    3: 'Metadata',
    4: 'LeaderAndIsr',
    5: 'StopReplica',
    6: 'UpdateMetadata',
    7: 'ControlledShutdown',
    8: 'OffsetCommit',
    9: 'OffsetFetch',
    10: 'FindCoordinator',
    11: 'JoinGroup',
    12: 'Heartbeat',
    13: 'LeaveGroup',
    14: 'SyncGroup',
    15: 'DescribeGroups',
    16: 'ListGroups',
    17: 'SaslHandshake',
    18: 'ApiVersions',
    19: 'CreateTopics',
    20: 'DeleteTopics',
    21: 'DeleteRecords',
    22: 'InitProducerId',
    23: 'OffsetForLeaderEpoch',
    24: 'AddPartitionsToTxn',
    25: 'AddOffsetsToTxn',
    26: 'EndTxn',
    27: 'WriteTxnMarkers',
    28: 'TxnOffsetCommit',
    29: 'DescribeAcls',
    30: 'CreateAcls',
    31: 'DeleteAcls',
    32: 'DescribeConfigs',
    33: 'AlterConfigs',
    36: 'SaslAuthenticate',
    37: 'CreatePartitions',
}
