# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class OperationResultProperties(Model):
    """The run operation result properties.

    :param start_time: The start time of the workflow scope repetition.
    :type start_time: datetime
    :param end_time: The end time of the workflow scope repetition.
    :type end_time: datetime
    :param correlation: The correlation properties.
    :type correlation: ~azure.mgmt.logic.models.RunActionCorrelation
    :param status: The status of the workflow scope repetition. Possible
     values include: 'NotSpecified', 'Paused', 'Running', 'Waiting',
     'Succeeded', 'Skipped', 'Suspended', 'Cancelled', 'Failed', 'Faulted',
     'TimedOut', 'Aborted', 'Ignored'
    :type status: str or ~azure.mgmt.logic.models.WorkflowStatus
    :param code: The workflow scope repetition code.
    :type code: str
    :param error:
    :type error: object
    """

    _attribute_map = {
        'start_time': {'key': 'startTime', 'type': 'iso-8601'},
        'end_time': {'key': 'endTime', 'type': 'iso-8601'},
        'correlation': {'key': 'correlation', 'type': 'RunActionCorrelation'},
        'status': {'key': 'status', 'type': 'WorkflowStatus'},
        'code': {'key': 'code', 'type': 'str'},
        'error': {'key': 'error', 'type': 'object'},
    }

    def __init__(self, *, start_time=None, end_time=None, correlation=None, status=None, code: str=None, error=None, **kwargs) -> None:
        super(OperationResultProperties, self).__init__(**kwargs)
        self.start_time = start_time
        self.end_time = end_time
        self.correlation = correlation
        self.status = status
        self.code = code
        self.error = error
