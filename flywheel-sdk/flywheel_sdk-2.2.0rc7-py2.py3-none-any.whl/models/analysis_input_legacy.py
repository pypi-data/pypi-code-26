# coding: utf-8

"""
    Flywheel

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: 2.2.0-rc.7
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


## NOTE: This file is auto generated by the swagger code generator program.
## Do not edit the file manually.

import pprint
import re  # noqa: F401

import six

from flywheel.models.file_entry import FileEntry  # noqa: F401,E501
from flywheel.models.note import Note  # noqa: F401,E501

# NOTE: This file is auto generated by the swagger code generator program.
# Do not edit the class manually.

class AnalysisInputLegacy(object):

    swagger_types = {
        'inputs': 'list[FileEntry]',
        'outputs': 'list[FileEntry]',
        'notes': 'list[Note]',
        'description': 'str',
        'label': 'str'
    }

    attribute_map = {
        'inputs': 'inputs',
        'outputs': 'outputs',
        'notes': 'notes',
        'description': 'description',
        'label': 'label'
    }

    rattribute_map = {
        'inputs': 'inputs',
        'outputs': 'outputs',
        'notes': 'notes',
        'description': 'description',
        'label': 'label'
    }

    def __init__(self, inputs=None, outputs=None, notes=None, description=None, label=None):  # noqa: E501
        """AnalysisInputLegacy - a model defined in Swagger"""

        self._inputs = None
        self._outputs = None
        self._notes = None
        self._description = None
        self._label = None
        self.discriminator = None

        if inputs is not None:
            self.inputs = inputs
        if outputs is not None:
            self.outputs = outputs
        if notes is not None:
            self.notes = notes
        if description is not None:
            self.description = description
        if label is not None:
            self.label = label

    @property
    def inputs(self):
        """Gets the inputs of this AnalysisInputLegacy.

        The set of inputs that this analysis is based on

        :return: The inputs of this AnalysisInputLegacy.
        :rtype: list[FileEntry]
        """
        return self._inputs

    @inputs.setter
    def inputs(self, inputs):
        """Sets the inputs of this AnalysisInputLegacy.

        The set of inputs that this analysis is based on

        :param inputs: The inputs of this AnalysisInputLegacy.  # noqa: E501
        :type: list[FileEntry]
        """

        self._inputs = inputs

    @property
    def outputs(self):
        """Gets the outputs of this AnalysisInputLegacy.


        :return: The outputs of this AnalysisInputLegacy.
        :rtype: list[FileEntry]
        """
        return self._outputs

    @outputs.setter
    def outputs(self, outputs):
        """Sets the outputs of this AnalysisInputLegacy.


        :param outputs: The outputs of this AnalysisInputLegacy.  # noqa: E501
        :type: list[FileEntry]
        """

        self._outputs = outputs

    @property
    def notes(self):
        """Gets the notes of this AnalysisInputLegacy.


        :return: The notes of this AnalysisInputLegacy.
        :rtype: list[Note]
        """
        return self._notes

    @notes.setter
    def notes(self, notes):
        """Sets the notes of this AnalysisInputLegacy.


        :param notes: The notes of this AnalysisInputLegacy.  # noqa: E501
        :type: list[Note]
        """

        self._notes = notes

    @property
    def description(self):
        """Gets the description of this AnalysisInputLegacy.


        :return: The description of this AnalysisInputLegacy.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this AnalysisInputLegacy.


        :param description: The description of this AnalysisInputLegacy.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def label(self):
        """Gets the label of this AnalysisInputLegacy.

        Application-specific label

        :return: The label of this AnalysisInputLegacy.
        :rtype: str
        """
        return self._label

    @label.setter
    def label(self, label):
        """Sets the label of this AnalysisInputLegacy.

        Application-specific label

        :param label: The label of this AnalysisInputLegacy.  # noqa: E501
        :type: str
        """
        if label is not None and len(label) > 256:
            raise ValueError("Invalid value for `label`, length must be less than or equal to `256`")  # noqa: E501
        if label is not None and len(label) < 1:
            raise ValueError("Invalid value for `label`, length must be greater than or equal to `1`")  # noqa: E501

        self._label = label


    @staticmethod
    def positional_to_model(value):
        """Converts a positional argument to a model value"""
        return value

    def return_value(self):
        """Unwraps return value from model"""
        return self

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
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
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, AnalysisInputLegacy):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

    # Container emulation
    def __getitem__(self, key):
        """Returns the value of key"""
        key = self._map_key(key)
        return getattr(self, key)

    def __setitem__(self, key, value):
        """Sets the value of key"""
        key = self._map_key(key)
        setattr(self, key, value)

    def __contains__(self, key):
        """Checks if the given value is a key in this object"""
        key = self._map_key(key, raise_on_error=False)
        return key is not None

    def keys(self):
        """Returns the list of json properties in the object"""
        return self.__class__.rattribute_map.keys()

    def values(self):
        """Returns the list of values in the object"""
        for key in self.__class__.attribute_map.keys():
            yield getattr(self, key)

    def items(self):
        """Returns the list of json property to value mapping"""
        for key, prop in self.__class__.rattribute_map.items():
            yield key, getattr(self, prop)

    def get(self, key, default=None):
        """Get the value of the provided json property, or default"""
        key = self._map_key(key, raise_on_error=False)
        if key:
            return getattr(self, key, default)
        return default

    def _map_key(self, key, raise_on_error=True):
        result = self.__class__.rattribute_map.get(key)
        if result is None:
            if raise_on_error:
                raise AttributeError('Invalid attribute name: {}'.format(key))
            return None
        return '_' + result
