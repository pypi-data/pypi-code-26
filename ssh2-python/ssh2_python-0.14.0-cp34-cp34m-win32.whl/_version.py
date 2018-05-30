
import json

version_json = '''
{"full-revisionid": "8adab6560072f454dc77b12f20e3b9d01e8b3a19", "date": "2018-05-30T14:24:19.735629", "error": null, "version": "0.14.0", "dirty": false}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

