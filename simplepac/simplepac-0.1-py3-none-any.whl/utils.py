import base64


def is_base64(text):
    try:
        base64.b64decode(text)
    except ValueError:
        return False
    return True


def get_mask(end):
    mask = ''
    end = int(end)
    mask += '.'.join(['255'] * int((end / 8)))
    if (32 - end) % 8 != 0:
        a = '1' * int(8 - (32 - end) % 8) + '0' * int((32 - end) % 8)
        mask += '.' + str(int(a, 2))

    b = int((32 - end) / 8) * '.0'
    mask += b
    return mask


__all__ = ['is_base64', 'get_mask']
