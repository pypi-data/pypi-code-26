import hashlib
from binascii import hexlify
from struct import pack, unpack, calcsize, error as structError


class _Frame(object):
    _major_version = 1
    _minor_version = 0
    _version_header = '<BB'
    _version_header_size = calcsize(_version_header)
    _1_0_format = '<32s16s34xI'
    _1_0_format_size = calcsize(_1_0_format)
    _full_1_0_format_header = "{}{}".format(_version_header, _1_0_format[1:])

    @staticmethod
    def hash(topic):
        btopic = topic.encode()
        hashed_obj = hashlib.sha256(btopic)
        hashed = hashed_obj.digest()
        return hashed

    @classmethod
    def pack(cls, topic, brewer_id, payload):
        fmt = "{}{}s".format(cls._full_1_0_format_header, len(payload))
        packed = pack(fmt,
                      cls._major_version, cls._minor_version,
                      cls.hash(topic), bytes.fromhex(brewer_id),
                      len(payload), payload)
        return packed

    @classmethod
    def unpack(cls, frame):
        # read major/minor versions
        try:
            major_version, minor_version = \
                unpack(cls._version_header,
                       frame[:cls._version_header_size])
        except structError:
            raise ValueError(
                "Unable to unpack version info from frame header {}".
                format(hexlify(frame))
            )

        if major_version > cls._major_version:
            raise ValueError("Major protocol version: '{}' does not match "
                             "supported version {}".
                             format(major_version, cls._major_version))
        parse_start = cls._version_header_size

        # start matching minor versions here

        try:
            topic, bid_bytes, payload_len = \
                unpack(cls._1_0_format,
                       frame[parse_start:parse_start+cls._1_0_format_size])
        except structError:
            raise ValueError(
                "Unable to unpack topic, brewer_id, or payload_length,"
                "info from frame header {}".format(hexlify(frame))
            )

        parse_start += cls._1_0_format_size

        try:
            payload, = \
                unpack('{}s'.format(payload_len), frame[parse_start:])
        except structError:
            raise ValueError(
                "Unable to unpack payload from frame (offset: {}, len: {}) {}".
                format(parse_start, payload_len, hexlify(frame))
            )

        try:
            return topic, hexlify(bid_bytes).decode(), payload
        except TypeError:
            raise ValueError("Unable to decode brewer_id")

        # once subsequent versions are known, above code could test against its
        # version while falling back at the end to newest known version


Frame = _Frame()
