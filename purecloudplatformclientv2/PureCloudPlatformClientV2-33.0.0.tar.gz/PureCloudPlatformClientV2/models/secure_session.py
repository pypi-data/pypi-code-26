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


class SecureSession(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self):
        """
        SecureSession - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'str',
            'flow': 'UriReference',
            'user_data': 'str',
            'state': 'str',
            'source_participant_id': 'str',
            'disconnect': 'bool',
            'self_uri': 'str'
        }

        self.attribute_map = {
            'id': 'id',
            'flow': 'flow',
            'user_data': 'userData',
            'state': 'state',
            'source_participant_id': 'sourceParticipantId',
            'disconnect': 'disconnect',
            'self_uri': 'selfUri'
        }

        self._id = None
        self._flow = None
        self._user_data = None
        self._state = None
        self._source_participant_id = None
        self._disconnect = None
        self._self_uri = None

    @property
    def id(self):
        """
        Gets the id of this SecureSession.
        The globally unique identifier for the object.

        :return: The id of this SecureSession.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this SecureSession.
        The globally unique identifier for the object.

        :param id: The id of this SecureSession.
        :type: str
        """
        
        self._id = id

    @property
    def flow(self):
        """
        Gets the flow of this SecureSession.
        The flow to execute securely

        :return: The flow of this SecureSession.
        :rtype: UriReference
        """
        return self._flow

    @flow.setter
    def flow(self, flow):
        """
        Sets the flow of this SecureSession.
        The flow to execute securely

        :param flow: The flow of this SecureSession.
        :type: UriReference
        """
        
        self._flow = flow

    @property
    def user_data(self):
        """
        Gets the user_data of this SecureSession.
        Customer-provided data

        :return: The user_data of this SecureSession.
        :rtype: str
        """
        return self._user_data

    @user_data.setter
    def user_data(self, user_data):
        """
        Sets the user_data of this SecureSession.
        Customer-provided data

        :param user_data: The user_data of this SecureSession.
        :type: str
        """
        
        self._user_data = user_data

    @property
    def state(self):
        """
        Gets the state of this SecureSession.
        The current state of a secure session

        :return: The state of this SecureSession.
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """
        Sets the state of this SecureSession.
        The current state of a secure session

        :param state: The state of this SecureSession.
        :type: str
        """
        allowed_values = ["PENDING", "COMPLETED", "FAILED"]
        if state.lower() not in map(str.lower, allowed_values):
            # print "Invalid value for state -> " + state
            self._state = "outdated_sdk_version"
        else:
            self._state = state

    @property
    def source_participant_id(self):
        """
        Gets the source_participant_id of this SecureSession.
        Unique identifier for the participant initiating the secure session.

        :return: The source_participant_id of this SecureSession.
        :rtype: str
        """
        return self._source_participant_id

    @source_participant_id.setter
    def source_participant_id(self, source_participant_id):
        """
        Sets the source_participant_id of this SecureSession.
        Unique identifier for the participant initiating the secure session.

        :param source_participant_id: The source_participant_id of this SecureSession.
        :type: str
        """
        
        self._source_participant_id = source_participant_id

    @property
    def disconnect(self):
        """
        Gets the disconnect of this SecureSession.
        If true, disconnect the agent after creating the session

        :return: The disconnect of this SecureSession.
        :rtype: bool
        """
        return self._disconnect

    @disconnect.setter
    def disconnect(self, disconnect):
        """
        Sets the disconnect of this SecureSession.
        If true, disconnect the agent after creating the session

        :param disconnect: The disconnect of this SecureSession.
        :type: bool
        """
        
        self._disconnect = disconnect

    @property
    def self_uri(self):
        """
        Gets the self_uri of this SecureSession.
        The URI for this object

        :return: The self_uri of this SecureSession.
        :rtype: str
        """
        return self._self_uri

    @self_uri.setter
    def self_uri(self, self_uri):
        """
        Sets the self_uri of this SecureSession.
        The URI for this object

        :param self_uri: The self_uri of this SecureSession.
        :type: str
        """
        
        self._self_uri = self_uri

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

