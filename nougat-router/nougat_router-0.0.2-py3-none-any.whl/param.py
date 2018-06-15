from .exceptions import *

from typing import Callable, Any, List


class Parameter:

    ALL_LOCATION = ['url', 'query', 'form', 'header', 'cookie']

    def __init__(self,
                 name: str,
                 type: Callable[[str], Any],
                 location: (str, List[str]) = 'query',
                 optional: bool =False,
                 default: Any =None,
                 action: str = None,
                 append: bool = False,
                 description: str = None,
                 warning: str = None):

        self.name = name
        self.type = type  # type or [type, type]
        self.location = location  # cookies, query, form, headers
        self.optional = optional  # true, false
        self.default = default  # if optional is true
        self.action = action  # rename
        self.append = append  # list or not
        self.description = description  # description
        self.warning = warning
        if self.optional and self.default is None:
            raise ParamNeedDefaultValueIfItsOptional()

        # location iterable
        if not isinstance(self.location, list):
            self.location = [self.location]
        unexpected_location = list(set(self.location) - set(Parameter.ALL_LOCATION))
        if unexpected_location:
            raise ParamComingFromUnknownLocation(self.name, unexpected_location)


class ParameterGroup:
    pass