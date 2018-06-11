"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""


PUBKEEPER_PROTOCOL_V10 = '1.0'
PUBKEEPER_PROTOCOL_V11 = '1.1'

protocol_version = PUBKEEPER_PROTOCOL_V11

supported_protocol_versions = [
    PUBKEEPER_PROTOCOL_V11,
    PUBKEEPER_PROTOCOL_V10,
]

protocol_flags = {
    'HIGH_LOW_LENGTH': 1 << 0
}
