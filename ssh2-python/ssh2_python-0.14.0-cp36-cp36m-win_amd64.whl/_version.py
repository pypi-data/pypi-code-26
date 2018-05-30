
import json

version_json = '''
{"date": "2018-05-30T14:57:57.846298", "dirty": false, "error": null, "full-revisionid": "8adab6560072f454dc77b12f20e3b9d01e8b3a19", "version": "0.14.0"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

