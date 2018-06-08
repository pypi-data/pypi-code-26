def parse_part(x):
    x = int(x)
    parts = []
    while x > 0:
        parts.append('%02x' % (x % 256))
        x = x >> 8
    return ''.join(parts)


def unparse_part(part):
    result = 0
    while len(part) > 0:
        part, x = part[:-2], part[-2:]
        result = (result + int(x, 16)) << 8
    return result >> 8


def get_uuid_parts(uuid):
    uuid = uuid.replace('-', '')
    low = unparse_part(uuid[:16])
    high = unparse_part(uuid[16:])
    return dict(low=low, high=high)


def get_uuid_string(low=None, high=None, **x):
    """This method parses a UUID protobuf message type from its component
    'high' and 'low' longs into a standard formatted UUID string

    Args:
        x (dict): containing keys, 'low' and 'high' corresponding to the UUID
            protobuf message type

    Returns:
        str: UUID formatted string
    """
    if low is None or high is None:
        return None
    x = ''.join([parse_part(low), parse_part(high)])
    return '-'.join([x[:8], x[8:12], x[12:16], x[16:20], x[20:32]])
