from jsondiff import diff
import json


def assert_json(expected_json, current_json, allow_unexpected_fields=True, allow_missing_fields=False):
    differences = json.loads(diff(expected_json, current_json, syntax='symmetric', dump=True))

    reserved_keynames = ["$delete", "$insert"]

    if not allow_missing_fields:
        if '$delete' in differences:
            raise ValueError('Some fields are missing')

    if not allow_unexpected_fields:
        if '$insert' in differences:
            raise ValueError('There are fields not expected')

    copied_differencies = differences.copy()

    for keyword in reserved_keynames:
        if keyword in copied_differencies:
            del copied_differencies[keyword]

    if len(copied_differencies) > 0:
        raise ValueError('Json documents doesn\'t match')
