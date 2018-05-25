import six
import sys

empty_str_val = '-'
empty_row_val = -1

defaults = {
    'sheet': empty_str_val,
    'column': empty_str_val,
    'row': empty_row_val,
    'message': empty_str_val,
    'value': empty_str_val,
}

def error(e):
    new_e = defaults.copy()
    new_e.update(e)
    if new_e['row'] != empty_row_val:
        # Add two for header row and 1-based counting
        new_e['row'] += 2
    return new_e


def error_sort_key(e):
    return [e[k] for k in ['sheet', 'column', 'row', 'message']]


def filter_first_seen(errors):
    errors_seen = set()
    filtered = []
    for e in errors:
        key = (e['sheet'], e['column'], e['message'])
        if key in errors_seen:
            continue
        errors_seen.add(key)
        filtered.append(e)
    return filtered


def stringify(e):
    e = e.copy()
    if isinstance(e['row'], six.integer_types) and e['row'] == empty_row_val:
        e['row'] = empty_str_val
    if (sys.version_info > (3, 0)):
        _str = str
    else:
        _str = unicode
    for k in e:
        e[k] = _str(e[k])
    return e
