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


class RecommendedElasticPoolMetric(Model):
    """Represents recommended elastic pool metric.

    :param date_time_property: The time of metric (ISO8601 format).
    :type date_time_property: datetime
    :param dtu: Gets or sets the DTUs (Database Transaction Units). See
     https://azure.microsoft.com/documentation/articles/sql-database-what-is-a-dtu/
    :type dtu: float
    :param size_gb: Gets or sets size in gigabytes.
    :type size_gb: float
    """

    _attribute_map = {
        'date_time_property': {'key': 'dateTime', 'type': 'iso-8601'},
        'dtu': {'key': 'dtu', 'type': 'float'},
        'size_gb': {'key': 'sizeGB', 'type': 'float'},
    }

    def __init__(self, *, date_time_property=None, dtu: float=None, size_gb: float=None, **kwargs) -> None:
        super(RecommendedElasticPoolMetric, self).__init__(**kwargs)
        self.date_time_property = date_time_property
        self.dtu = dtu
        self.size_gb = size_gb
