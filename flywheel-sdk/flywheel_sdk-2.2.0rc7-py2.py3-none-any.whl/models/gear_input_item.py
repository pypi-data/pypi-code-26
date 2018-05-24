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

# NOTE: This file is auto generated by the swagger code generator program.
# Do not edit the class manually.

class GearInputItem(object):

    swagger_types = {
        'base': 'str',
        'description': 'str',
        'optional': 'bool'
    }

    attribute_map = {
        'base': 'base',
        'description': 'description',
        'optional': 'optional'
    }

    rattribute_map = {
        'base': 'base',
        'description': 'description',
        'optional': 'optional'
    }

    def __init__(self, base=None, description=None, optional=None):  # noqa: E501
        """GearInputItem - a model defined in Swagger"""

        self._base = None
        self._description = None
        self._optional = None
        self.discriminator = None

        self.base = base
        if description is not None:
            self.description = description
        if optional is not None:
            self.optional = optional

    @property
    def base(self):
        """Gets the base of this GearInputItem.

        The type of gear input.

        :return: The base of this GearInputItem.
        :rtype: str
        """
        return self._base

    @base.setter
    def base(self, base):
        """Sets the base of this GearInputItem.

        The type of gear input.

        :param base: The base of this GearInputItem.  # noqa: E501
        :type: str
        """
        if base is None:
            raise ValueError("Invalid value for `base`, must not be `None`")  # noqa: E501
        allowed_values = ["file", "api-key"]  # noqa: E501
        if base not in allowed_values:
            raise ValueError(
                "Invalid value for `base` ({0}), must be one of {1}"  # noqa: E501
                .format(base, allowed_values)
            )

        self._base = base

    @property
    def description(self):
        """Gets the description of this GearInputItem.

        Hackaround for description not technically being a schema directive

        :return: The description of this GearInputItem.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this GearInputItem.

        Hackaround for description not technically being a schema directive

        :param description: The description of this GearInputItem.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def optional(self):
        """Gets the optional of this GearInputItem.

        Allow the gear to mark an input file as optional.

        :return: The optional of this GearInputItem.
        :rtype: bool
        """
        return self._optional

    @optional.setter
    def optional(self, optional):
        """Sets the optional of this GearInputItem.

        Allow the gear to mark an input file as optional.

        :param optional: The optional of this GearInputItem.  # noqa: E501
        :type: bool
        """

        self._optional = optional


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
        if not isinstance(other, GearInputItem):
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
