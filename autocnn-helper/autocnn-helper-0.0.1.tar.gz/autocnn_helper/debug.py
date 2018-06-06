import json
import os


def debug_write_parameter(parameter):
    os.environ['AUTOCNN_PARAMETER'] = json.dumps(parameter)
