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

from flywheel.models.job_config import JobConfig  # noqa: F401,E501
from flywheel.models.job_origin import JobOrigin  # noqa: F401,E501

# NOTE: This file is auto generated by the swagger code generator program.
# Do not edit the class manually.

class Batch(object):

    swagger_types = {
        'id': 'str',
        'gear_id': 'str',
        'state': 'str',
        'origin': 'JobOrigin',
        'config': 'JobConfig',
        'jobs': 'list[str]',
        'created': 'datetime',
        'modified': 'datetime'
    }

    attribute_map = {
        'id': '_id',
        'gear_id': 'gear_id',
        'state': 'state',
        'origin': 'origin',
        'config': 'config',
        'jobs': 'jobs',
        'created': 'created',
        'modified': 'modified'
    }

    rattribute_map = {
        '_id': 'id',
        'gear_id': 'gear_id',
        'state': 'state',
        'origin': 'origin',
        'config': 'config',
        'jobs': 'jobs',
        'created': 'created',
        'modified': 'modified'
    }

    def __init__(self, id=None, gear_id=None, state=None, origin=None, config=None, jobs=None, created=None, modified=None):  # noqa: E501
        """Batch - a model defined in Swagger"""

        self._id = None
        self._gear_id = None
        self._state = None
        self._origin = None
        self._config = None
        self._jobs = None
        self._created = None
        self._modified = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if gear_id is not None:
            self.gear_id = gear_id
        if state is not None:
            self.state = state
        if origin is not None:
            self.origin = origin
        if config is not None:
            self.config = config
        if jobs is not None:
            self.jobs = jobs
        if created is not None:
            self.created = created
        if modified is not None:
            self.modified = modified

    @property
    def id(self):
        """Gets the id of this Batch.

        Unique database ID

        :return: The id of this Batch.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Batch.

        Unique database ID

        :param id: The id of this Batch.  # noqa: E501
        :type: str
        """
        if id is not None and not re.search('^[a-fA-F0-9]{24}$', id):  # noqa: E501
            raise ValueError("Invalid value for `id`, must be a follow pattern or equal to `/^[a-fA-F0-9]{24}$/`")  # noqa: E501

        self._id = id

    @property
    def gear_id(self):
        """Gets the gear_id of this Batch.


        :return: The gear_id of this Batch.
        :rtype: str
        """
        return self._gear_id

    @gear_id.setter
    def gear_id(self, gear_id):
        """Sets the gear_id of this Batch.


        :param gear_id: The gear_id of this Batch.  # noqa: E501
        :type: str
        """

        self._gear_id = gear_id

    @property
    def state(self):
        """Gets the state of this Batch.


        :return: The state of this Batch.
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this Batch.


        :param state: The state of this Batch.  # noqa: E501
        :type: str
        """
        allowed_values = ["pending", "running", "failed", "complete", "cancelled"]  # noqa: E501
        if state not in allowed_values:
            raise ValueError(
                "Invalid value for `state` ({0}), must be one of {1}"  # noqa: E501
                .format(state, allowed_values)
            )

        self._state = state

    @property
    def origin(self):
        """Gets the origin of this Batch.


        :return: The origin of this Batch.
        :rtype: JobOrigin
        """
        return self._origin

    @origin.setter
    def origin(self, origin):
        """Sets the origin of this Batch.


        :param origin: The origin of this Batch.  # noqa: E501
        :type: JobOrigin
        """

        self._origin = origin

    @property
    def config(self):
        """Gets the config of this Batch.


        :return: The config of this Batch.
        :rtype: JobConfig
        """
        return self._config

    @config.setter
    def config(self, config):
        """Sets the config of this Batch.


        :param config: The config of this Batch.  # noqa: E501
        :type: JobConfig
        """

        self._config = config

    @property
    def jobs(self):
        """Gets the jobs of this Batch.


        :return: The jobs of this Batch.
        :rtype: list[str]
        """
        return self._jobs

    @jobs.setter
    def jobs(self, jobs):
        """Sets the jobs of this Batch.


        :param jobs: The jobs of this Batch.  # noqa: E501
        :type: list[str]
        """

        self._jobs = jobs

    @property
    def created(self):
        """Gets the created of this Batch.

        Creation time (automatically set)

        :return: The created of this Batch.
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """Sets the created of this Batch.

        Creation time (automatically set)

        :param created: The created of this Batch.  # noqa: E501
        :type: datetime
        """

        self._created = created

    @property
    def modified(self):
        """Gets the modified of this Batch.

        Last modification time (automatically updated)

        :return: The modified of this Batch.
        :rtype: datetime
        """
        return self._modified

    @modified.setter
    def modified(self, modified):
        """Sets the modified of this Batch.

        Last modification time (automatically updated)

        :param modified: The modified of this Batch.  # noqa: E501
        :type: datetime
        """

        self._modified = modified


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
        if not isinstance(other, Batch):
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
