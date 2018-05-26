# coding: utf-8

"""
Copyright 2016 SmartBear Software

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Ref: https://github.com/swagger-api/swagger-codegen
"""

from pprint import pformat
from six import iteritems
import re


class AnalyticsRoutingStatusRecord(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self):
        """
        AnalyticsRoutingStatusRecord - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'start_time': 'datetime',
            'end_time': 'datetime',
            'routing_status': 'str',
            'duration_milliseconds': 'int'
        }

        self.attribute_map = {
            'start_time': 'startTime',
            'end_time': 'endTime',
            'routing_status': 'routingStatus',
            'duration_milliseconds': 'durationMilliseconds'
        }

        self._start_time = None
        self._end_time = None
        self._routing_status = None
        self._duration_milliseconds = None

    @property
    def start_time(self):
        """
        Gets the start_time of this AnalyticsRoutingStatusRecord.
        The start time of the record. Date time is represented as an ISO-8601 string. For example: yyyy-MM-ddTHH:mm:ss.SSSZ

        :return: The start_time of this AnalyticsRoutingStatusRecord.
        :rtype: datetime
        """
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        """
        Sets the start_time of this AnalyticsRoutingStatusRecord.
        The start time of the record. Date time is represented as an ISO-8601 string. For example: yyyy-MM-ddTHH:mm:ss.SSSZ

        :param start_time: The start_time of this AnalyticsRoutingStatusRecord.
        :type: datetime
        """
        
        self._start_time = start_time

    @property
    def end_time(self):
        """
        Gets the end_time of this AnalyticsRoutingStatusRecord.
        The end time of the record. Date time is represented as an ISO-8601 string. For example: yyyy-MM-ddTHH:mm:ss.SSSZ

        :return: The end_time of this AnalyticsRoutingStatusRecord.
        :rtype: datetime
        """
        return self._end_time

    @end_time.setter
    def end_time(self, end_time):
        """
        Sets the end_time of this AnalyticsRoutingStatusRecord.
        The end time of the record. Date time is represented as an ISO-8601 string. For example: yyyy-MM-ddTHH:mm:ss.SSSZ

        :param end_time: The end_time of this AnalyticsRoutingStatusRecord.
        :type: datetime
        """
        
        self._end_time = end_time

    @property
    def routing_status(self):
        """
        Gets the routing_status of this AnalyticsRoutingStatusRecord.
        The user's ACD routing status

        :return: The routing_status of this AnalyticsRoutingStatusRecord.
        :rtype: str
        """
        return self._routing_status

    @routing_status.setter
    def routing_status(self, routing_status):
        """
        Sets the routing_status of this AnalyticsRoutingStatusRecord.
        The user's ACD routing status

        :param routing_status: The routing_status of this AnalyticsRoutingStatusRecord.
        :type: str
        """
        allowed_values = ["OFF_QUEUE", "IDLE", "INTERACTING", "NOT_RESPONDING", "COMMUNICATING"]
        if routing_status.lower() not in map(str.lower, allowed_values):
            # print "Invalid value for routing_status -> " + routing_status
            self._routing_status = "outdated_sdk_version"
        else:
            self._routing_status = routing_status

    @property
    def duration_milliseconds(self):
        """
        Gets the duration_milliseconds of this AnalyticsRoutingStatusRecord.
        The duration of the status (in milliseconds)

        :return: The duration_milliseconds of this AnalyticsRoutingStatusRecord.
        :rtype: int
        """
        return self._duration_milliseconds

    @duration_milliseconds.setter
    def duration_milliseconds(self, duration_milliseconds):
        """
        Sets the duration_milliseconds of this AnalyticsRoutingStatusRecord.
        The duration of the status (in milliseconds)

        :param duration_milliseconds: The duration_milliseconds of this AnalyticsRoutingStatusRecord.
        :type: int
        """
        
        self._duration_milliseconds = duration_milliseconds

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other

