row_conversion_map = {"L": int, "f": float}


def format_row(fmt, row):
    ret = []
    fmt = fmt[-len(row) :]
    for char, item in zip(fmt, row):
        converter = row_conversion_map.get(char)
        if converter is None:
            ret.append(item)
        else:
            ret.append(converter(item))
    return ret


def readings_by_identifier(readings):
    ret = {}
    for r in readings:
        if r.point_number not in ret:
            ret[r.point_number] = []

        ret[r.point_number].append(r)
    return ret
