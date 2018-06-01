
import datetime
import json
import subprocess
from firstdown_cloud import s3


def expected_output_is_present(command, expected_text):
    console_output = subprocess.check_output(command, shell=True)
    return expected_text in console_output

def upload_service_status(command, expected_output, bucket, key):
    status = expected_output_is_present(command, expected_output)
    statusDict = {'active': status, "timestamp":  datetime.datetime.now().isoformat()}
    s3.put_object(bucket, key, json.dumps(statusDict, indent=4, sort_keys=True))
    return statusDict

