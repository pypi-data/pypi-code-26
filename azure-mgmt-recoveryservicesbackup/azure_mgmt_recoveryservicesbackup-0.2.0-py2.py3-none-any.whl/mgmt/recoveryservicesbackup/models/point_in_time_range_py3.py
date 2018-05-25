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


class PointInTimeRange(Model):
    """Provides details for log ranges.

    :param start_time: Start time of the time range for log recovery.
    :type start_time: datetime
    :param end_time: End time of the time range for log recovery.
    :type end_time: datetime
    """

    _attribute_map = {
        'start_time': {'key': 'startTime', 'type': 'iso-8601'},
        'end_time': {'key': 'endTime', 'type': 'iso-8601'},
    }

    def __init__(self, *, start_time=None, end_time=None, **kwargs) -> None:
        super(PointInTimeRange, self).__init__(**kwargs)
        self.start_time = start_time
        self.end_time = end_time
