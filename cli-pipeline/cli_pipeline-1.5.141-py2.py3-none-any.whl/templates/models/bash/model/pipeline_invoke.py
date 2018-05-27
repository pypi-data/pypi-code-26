import os
import numpy as np
import json
import logging

from pipeline_monitor import prometheus_monitor as monitor
from pipeline_logger import log

_logger = logging.getLogger('pipeline-logger')
_logger.setLevel(logging.INFO)
_logger_stream_handler = logging.StreamHandler()
_logger_stream_handler.setLevel(logging.INFO)
_logger.addHandler(_logger_stream_handler)


__all__ = ['invoke']


_labels = {
           'model_name': '{{ PIPELINE_MODEL_NAME }}',
           'model_tag': '{{ PIPELINE_MODEL_TAG }}',
           'model_type': '{{ PIPELINE_MODEL_TYPE }}',
           'model_runtime': '{{ PIPELINE_MODEL_RUNTIME }}',
           'model_chip': '{{ PIPELINE_MODEL_CHIP }}',
          }


@log(labels=_labels, logger=_logger)
def invoke(request):
    '''Where the magic happens...'''

    with monitor(labels=_labels, name="transform_request"):
        transformed_request = _transform_request(request)

    with monitor(labels=_labels, name="invoke"):
        cmd = "pipeline_invoke.sh %s" % transformed_request
        response_bytes = _subprocess.check_output(cmd, shell=True)
        response = response_bytes.decode('utf-8')    

    with monitor(labels=_labels, name="transform_response"):
        transformed_response = _transform_response(response)

    return transformed_response


def _transform_request(request):
    # Convert from bytes to tf.tensor, np.array, etc.
    return request


def _transform_response(response):
    # Convert from tf.tensor, np.array, etc. to bytes
    return response 
