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


class ConversationQuery(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self):
        """
        ConversationQuery - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'interval': 'str',
            'conversation_filters': 'list[AnalyticsQueryFilter]',
            'evaluation_filters': 'list[AnalyticsQueryFilter]',
            'segment_filters': 'list[AnalyticsQueryFilter]',
            'aggregations': 'list[AnalyticsQueryAggregation]',
            'paging': 'PagingSpec',
            'order': 'str',
            'order_by': 'str'
        }

        self.attribute_map = {
            'interval': 'interval',
            'conversation_filters': 'conversationFilters',
            'evaluation_filters': 'evaluationFilters',
            'segment_filters': 'segmentFilters',
            'aggregations': 'aggregations',
            'paging': 'paging',
            'order': 'order',
            'order_by': 'orderBy'
        }

        self._interval = None
        self._conversation_filters = None
        self._evaluation_filters = None
        self._segment_filters = None
        self._aggregations = None
        self._paging = None
        self._order = None
        self._order_by = None

    @property
    def interval(self):
        """
        Gets the interval of this ConversationQuery.
        Specifies the date and time range of data being queried. Results will include conversations that started, ended, or had any activity during the interval. Intervals are represented as an ISO-8601 string. For example: YYYY-MM-DDThh:mm:ss/YYYY-MM-DDThh:mm:ss

        :return: The interval of this ConversationQuery.
        :rtype: str
        """
        return self._interval

    @interval.setter
    def interval(self, interval):
        """
        Sets the interval of this ConversationQuery.
        Specifies the date and time range of data being queried. Results will include conversations that started, ended, or had any activity during the interval. Intervals are represented as an ISO-8601 string. For example: YYYY-MM-DDThh:mm:ss/YYYY-MM-DDThh:mm:ss

        :param interval: The interval of this ConversationQuery.
        :type: str
        """
        
        self._interval = interval

    @property
    def conversation_filters(self):
        """
        Gets the conversation_filters of this ConversationQuery.
        Filters that target conversation-level data

        :return: The conversation_filters of this ConversationQuery.
        :rtype: list[AnalyticsQueryFilter]
        """
        return self._conversation_filters

    @conversation_filters.setter
    def conversation_filters(self, conversation_filters):
        """
        Sets the conversation_filters of this ConversationQuery.
        Filters that target conversation-level data

        :param conversation_filters: The conversation_filters of this ConversationQuery.
        :type: list[AnalyticsQueryFilter]
        """
        
        self._conversation_filters = conversation_filters

    @property
    def evaluation_filters(self):
        """
        Gets the evaluation_filters of this ConversationQuery.
        Filters that target quality management evaluation-level data

        :return: The evaluation_filters of this ConversationQuery.
        :rtype: list[AnalyticsQueryFilter]
        """
        return self._evaluation_filters

    @evaluation_filters.setter
    def evaluation_filters(self, evaluation_filters):
        """
        Sets the evaluation_filters of this ConversationQuery.
        Filters that target quality management evaluation-level data

        :param evaluation_filters: The evaluation_filters of this ConversationQuery.
        :type: list[AnalyticsQueryFilter]
        """
        
        self._evaluation_filters = evaluation_filters

    @property
    def segment_filters(self):
        """
        Gets the segment_filters of this ConversationQuery.
        Filters that target individual segments within a conversation

        :return: The segment_filters of this ConversationQuery.
        :rtype: list[AnalyticsQueryFilter]
        """
        return self._segment_filters

    @segment_filters.setter
    def segment_filters(self, segment_filters):
        """
        Sets the segment_filters of this ConversationQuery.
        Filters that target individual segments within a conversation

        :param segment_filters: The segment_filters of this ConversationQuery.
        :type: list[AnalyticsQueryFilter]
        """
        
        self._segment_filters = segment_filters

    @property
    def aggregations(self):
        """
        Gets the aggregations of this ConversationQuery.
        Include faceted search and aggregate roll-ups describing your search results. This does not function as a filter, but rather, summary data about the data matching your filters

        :return: The aggregations of this ConversationQuery.
        :rtype: list[AnalyticsQueryAggregation]
        """
        return self._aggregations

    @aggregations.setter
    def aggregations(self, aggregations):
        """
        Sets the aggregations of this ConversationQuery.
        Include faceted search and aggregate roll-ups describing your search results. This does not function as a filter, but rather, summary data about the data matching your filters

        :param aggregations: The aggregations of this ConversationQuery.
        :type: list[AnalyticsQueryAggregation]
        """
        
        self._aggregations = aggregations

    @property
    def paging(self):
        """
        Gets the paging of this ConversationQuery.
        Page size and number to control iterating through large result sets. Default page size is 25

        :return: The paging of this ConversationQuery.
        :rtype: PagingSpec
        """
        return self._paging

    @paging.setter
    def paging(self, paging):
        """
        Sets the paging of this ConversationQuery.
        Page size and number to control iterating through large result sets. Default page size is 25

        :param paging: The paging of this ConversationQuery.
        :type: PagingSpec
        """
        
        self._paging = paging

    @property
    def order(self):
        """
        Gets the order of this ConversationQuery.
        Sort the result set in ascending/descending order. Default is ascending

        :return: The order of this ConversationQuery.
        :rtype: str
        """
        return self._order

    @order.setter
    def order(self, order):
        """
        Sets the order of this ConversationQuery.
        Sort the result set in ascending/descending order. Default is ascending

        :param order: The order of this ConversationQuery.
        :type: str
        """
        allowed_values = ["asc", "desc"]
        if order.lower() not in map(str.lower, allowed_values):
            # print "Invalid value for order -> " + order
            self._order = "outdated_sdk_version"
        else:
            self._order = order

    @property
    def order_by(self):
        """
        Gets the order_by of this ConversationQuery.
        Specify which data element within the result set to use for sorting. The options  to use as a basis for sorting the results: conversationStart, segmentStart, and segmentEnd. If not specified, the default is conversationStart

        :return: The order_by of this ConversationQuery.
        :rtype: str
        """
        return self._order_by

    @order_by.setter
    def order_by(self, order_by):
        """
        Sets the order_by of this ConversationQuery.
        Specify which data element within the result set to use for sorting. The options  to use as a basis for sorting the results: conversationStart, segmentStart, and segmentEnd. If not specified, the default is conversationStart

        :param order_by: The order_by of this ConversationQuery.
        :type: str
        """
        allowed_values = ["conversationStart", "conversationEnd", "segmentStart", "segmentEnd"]
        if order_by.lower() not in map(str.lower, allowed_values):
            # print "Invalid value for order_by -> " + order_by
            self._order_by = "outdated_sdk_version"
        else:
            self._order_by = order_by

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

