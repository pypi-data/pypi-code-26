"""LICENSE
Copyright 2015 Hermann Krumrey <hermann@krumreyh.com>

This file is part of toktokkie.

toktokkie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

toktokkie is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with toktokkie.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from typing import List


class MetaType:
    """
    All metadata parameters must implement a to_json method
    """

    def to_json(self) -> any:
        """
        Converts the object into a JSON-compatible object.
        By default, the object itself will be returned
        :return: A JSON-compatible representation of the object
        """
        return self

    @classmethod
    def from_json(cls, json_data: any):
        """
        Generates a MetaType from a JSON element.
        By default, the json data is simply passed on to the constructor
        :param json_data: The JSON data to use
        :return: The generated object
        """
        # noinspection PyArgumentList
        return cls(json_data)


# noinspection PyAbstractClass
class MetaPrimitive(MetaType):
    """
    A class that, in addition to a to_json method, requires the implementation
    of a parse() method that parses a string and generates a corresponding
    object
    """

    @classmethod
    def parse(cls, string: str):
        """
        Parses a string to generate an object
        By default, the string is simply used as the only parameter of
        the constructor.
        :param string: The string
        :return: The generates object
        """
        # noinspection PyArgumentList
        return cls(string)


class Str(str, MetaPrimitive):
    """
    A class that implements a String primitive
    """
    pass


class Int(int, MetaPrimitive):
    """
    A class that implements an Integer primitive
    """
    pass


class MetaList(MetaType):
    """
    A class that acts as a list that can easily json-ify its content
    """

    def __init__(self, _list: List[MetaType]):
        """
        Initializes the internal list
        :param _list: The internal list
        """
        self.list = _list

    def append(self, element: MetaType):
        """
        Appends an element to the list
        :param element: The element to append
        :return: None
        """
        self.list.append(element)

    def pop(self, index: int) -> MetaType:
        """
        Removes an element of the list
        :param index: The index at which to remove the element
        :return: The removed element
        """
        return self.list.pop(index)

    def to_json(self) -> List[any]:
        """
        Converts the list to a JSON-compatible list
        :return: The JSON list
        """
        data = []
        for element in self.list:
            data.append(element.to_json())
        return data
