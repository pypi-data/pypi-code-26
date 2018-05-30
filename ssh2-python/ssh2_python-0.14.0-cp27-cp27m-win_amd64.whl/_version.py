
import json

version_json = '''
{"date": "2018-05-30T14:21:47.919000", "full-revisionid": "8adab6560072f454dc77b12f20e3b9d01e8b3a19", "dirty": false, "version": "0.14.0", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

