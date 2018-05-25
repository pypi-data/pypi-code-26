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


class MonitorConfigExpectedStatusCodeRangesItem(Model):
    """Min and max value of a status code range.

    :param min: Min status code.
    :type min: int
    :param max: Max status code.
    :type max: int
    """

    _attribute_map = {
        'min': {'key': 'min', 'type': 'int'},
        'max': {'key': 'max', 'type': 'int'},
    }

    def __init__(self, **kwargs):
        super(MonitorConfigExpectedStatusCodeRangesItem, self).__init__(**kwargs)
        self.min = kwargs.get('min', None)
        self.max = kwargs.get('max', None)
