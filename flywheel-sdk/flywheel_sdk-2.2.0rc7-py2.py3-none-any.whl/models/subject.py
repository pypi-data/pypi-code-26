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

from flywheel.models.common_info import CommonInfo  # noqa: F401,E501
from flywheel.models.file_entry import FileEntry  # noqa: F401,E501

# NOTE: This file is auto generated by the swagger code generator program.
# Do not edit the class manually.

class Subject(object):

    swagger_types = {
        'id': 'str',
        'firstname': 'str',
        'lastname': 'str',
        'age': 'int',
        'sex': 'str',
        'race': 'str',
        'ethnicity': 'str',
        'code': 'str',
        'tags': 'list[str]',
        'info': 'CommonInfo',
        'files': 'list[FileEntry]',
        'info_exists': 'bool'
    }

    attribute_map = {
        'id': '_id',
        'firstname': 'firstname',
        'lastname': 'lastname',
        'age': 'age',
        'sex': 'sex',
        'race': 'race',
        'ethnicity': 'ethnicity',
        'code': 'code',
        'tags': 'tags',
        'info': 'info',
        'files': 'files',
        'info_exists': 'info_exists'
    }

    rattribute_map = {
        '_id': 'id',
        'firstname': 'firstname',
        'lastname': 'lastname',
        'age': 'age',
        'sex': 'sex',
        'race': 'race',
        'ethnicity': 'ethnicity',
        'code': 'code',
        'tags': 'tags',
        'info': 'info',
        'files': 'files',
        'info_exists': 'info_exists'
    }

    def __init__(self, id=None, firstname=None, lastname=None, age=None, sex=None, race=None, ethnicity=None, code=None, tags=None, info=None, files=None, info_exists=None):  # noqa: E501
        """Subject - a model defined in Swagger"""

        self._id = None
        self._firstname = None
        self._lastname = None
        self._age = None
        self._sex = None
        self._race = None
        self._ethnicity = None
        self._code = None
        self._tags = None
        self._info = None
        self._files = None
        self._info_exists = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if firstname is not None:
            self.firstname = firstname
        if lastname is not None:
            self.lastname = lastname
        if age is not None:
            self.age = age
        if sex is not None:
            self.sex = sex
        if race is not None:
            self.race = race
        if ethnicity is not None:
            self.ethnicity = ethnicity
        if code is not None:
            self.code = code
        if tags is not None:
            self.tags = tags
        if info is not None:
            self.info = info
        if files is not None:
            self.files = files
        if info_exists is not None:
            self.info_exists = info_exists

    @property
    def id(self):
        """Gets the id of this Subject.

        Unique database ID

        :return: The id of this Subject.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Subject.

        Unique database ID

        :param id: The id of this Subject.  # noqa: E501
        :type: str
        """
        if id is not None and not re.search('^[a-fA-F0-9]{24}$', id):  # noqa: E501
            raise ValueError("Invalid value for `id`, must be a follow pattern or equal to `/^[a-fA-F0-9]{24}$/`")  # noqa: E501

        self._id = id

    @property
    def firstname(self):
        """Gets the firstname of this Subject.

        First name

        :return: The firstname of this Subject.
        :rtype: str
        """
        return self._firstname

    @firstname.setter
    def firstname(self, firstname):
        """Sets the firstname of this Subject.

        First name

        :param firstname: The firstname of this Subject.  # noqa: E501
        :type: str
        """
        if firstname is not None and len(firstname) > 64:
            raise ValueError("Invalid value for `firstname`, length must be less than or equal to `64`")  # noqa: E501

        self._firstname = firstname

    @property
    def lastname(self):
        """Gets the lastname of this Subject.

        Last name

        :return: The lastname of this Subject.
        :rtype: str
        """
        return self._lastname

    @lastname.setter
    def lastname(self, lastname):
        """Sets the lastname of this Subject.

        Last name

        :param lastname: The lastname of this Subject.  # noqa: E501
        :type: str
        """
        if lastname is not None and len(lastname) > 64:
            raise ValueError("Invalid value for `lastname`, length must be less than or equal to `64`")  # noqa: E501

        self._lastname = lastname

    @property
    def age(self):
        """Gets the age of this Subject.

        Age at time of session, in seconds

        :return: The age of this Subject.
        :rtype: int
        """
        return self._age

    @age.setter
    def age(self, age):
        """Sets the age of this Subject.

        Age at time of session, in seconds

        :param age: The age of this Subject.  # noqa: E501
        :type: int
        """

        self._age = age

    @property
    def sex(self):
        """Gets the sex of this Subject.


        :return: The sex of this Subject.
        :rtype: str
        """
        return self._sex

    @sex.setter
    def sex(self, sex):
        """Sets the sex of this Subject.


        :param sex: The sex of this Subject.  # noqa: E501
        :type: str
        """
        allowed_values = ["male", "female", "other", "unknown"]  # noqa: E501
        if sex not in allowed_values:
            raise ValueError(
                "Invalid value for `sex` ({0}), must be one of {1}"  # noqa: E501
                .format(sex, allowed_values)
            )

        self._sex = sex

    @property
    def race(self):
        """Gets the race of this Subject.


        :return: The race of this Subject.
        :rtype: str
        """
        return self._race

    @race.setter
    def race(self, race):
        """Sets the race of this Subject.


        :param race: The race of this Subject.  # noqa: E501
        :type: str
        """
        allowed_values = ["American Indian or Alaska Native", "Asian", "Native Hawaiian or Other Pacific Islander", "Black or African American", "White", "More Than One Race", "Unknown or Not Reported"]  # noqa: E501
        if race not in allowed_values:
            raise ValueError(
                "Invalid value for `race` ({0}), must be one of {1}"  # noqa: E501
                .format(race, allowed_values)
            )

        self._race = race

    @property
    def ethnicity(self):
        """Gets the ethnicity of this Subject.


        :return: The ethnicity of this Subject.
        :rtype: str
        """
        return self._ethnicity

    @ethnicity.setter
    def ethnicity(self, ethnicity):
        """Sets the ethnicity of this Subject.


        :param ethnicity: The ethnicity of this Subject.  # noqa: E501
        :type: str
        """
        allowed_values = ["Not Hispanic or Latino", "Hispanic or Latino", "Unknown or Not Reported"]  # noqa: E501
        if ethnicity not in allowed_values:
            raise ValueError(
                "Invalid value for `ethnicity` ({0}), must be one of {1}"  # noqa: E501
                .format(ethnicity, allowed_values)
            )

        self._ethnicity = ethnicity

    @property
    def code(self):
        """Gets the code of this Subject.

        A unique identifier for the subject

        :return: The code of this Subject.
        :rtype: str
        """
        return self._code

    @code.setter
    def code(self, code):
        """Sets the code of this Subject.

        A unique identifier for the subject

        :param code: The code of this Subject.  # noqa: E501
        :type: str
        """
        if code is not None and len(code) > 64:
            raise ValueError("Invalid value for `code`, length must be less than or equal to `64`")  # noqa: E501

        self._code = code

    @property
    def tags(self):
        """Gets the tags of this Subject.

        Array of application-specific tags

        :return: The tags of this Subject.
        :rtype: list[str]
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Sets the tags of this Subject.

        Array of application-specific tags

        :param tags: The tags of this Subject.  # noqa: E501
        :type: list[str]
        """

        self._tags = tags

    @property
    def info(self):
        """Gets the info of this Subject.


        :return: The info of this Subject.
        :rtype: CommonInfo
        """
        return self._info

    @info.setter
    def info(self, info):
        """Sets the info of this Subject.


        :param info: The info of this Subject.  # noqa: E501
        :type: CommonInfo
        """

        self._info = info

    @property
    def files(self):
        """Gets the files of this Subject.


        :return: The files of this Subject.
        :rtype: list[FileEntry]
        """
        return self._files

    @files.setter
    def files(self, files):
        """Sets the files of this Subject.


        :param files: The files of this Subject.  # noqa: E501
        :type: list[FileEntry]
        """

        self._files = files

    @property
    def info_exists(self):
        """Gets the info_exists of this Subject.

        Flag that indicates whether or not info exists on this container

        :return: The info_exists of this Subject.
        :rtype: bool
        """
        return self._info_exists

    @info_exists.setter
    def info_exists(self, info_exists):
        """Sets the info_exists of this Subject.

        Flag that indicates whether or not info exists on this container

        :param info_exists: The info_exists of this Subject.  # noqa: E501
        :type: bool
        """

        self._info_exists = info_exists


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
        if not isinstance(other, Subject):
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
