from .param import Parameter
from .exceptions import ParamRedefineException

import re
from typing import List, Dict, Callable, Any, Union, Tuple

DYNAMIC_ROUTE_PATTERN = re.compile(r"(:(?P<name>[a-zA-Z_]+)(<(?P<regex>.+)>)?)+")


class Route:

    def __init__(self, method, url, controller):

        self.method: str = method
        self.__prefix: str = None
        self.__url: str = None

        self.pattern = None

        self.params: Dict[str, Parameter] = {}

        self.controller = controller

        self.url = url

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):

        self.__url = value
        if value:
            self.__url_pattern_generator()

    @property
    def prefix(self):
        return self.__prefix

    @prefix.setter
    def prefix(self, value):
        self.url = '{}{}'.format(value, self.url)

    def __url_pattern_generator(self):
        route = self.__url
        parameters: List[Tuple[str, str, str, str]] = DYNAMIC_ROUTE_PATTERN.findall(route)
        parameters_pattern: List[Tuple[str, str]] = [(old, "(?P<{}>{})".format(name, pattern or '[^/]+')) for
                                                     (old, name, _, pattern) in parameters]
        route_pattern: str = route
        for old, param_pattern in parameters_pattern:
            route_pattern = route_pattern.replace(old, param_pattern)

        self.pattern = re.compile(route_pattern)

    def add_param(self,
                  name: str,
                  type: Callable[[str], Any],
                  location: Union[str, List[str]] = 'query',
                  optional: bool = False,
                  default: Any = None,
                  action=None,
                  append=False,
                  description: str = None,
                  warning: str = None
                  ) -> None:

        if name in self.params:
            raise ParamRedefineException(
                self.method,
                self.url,
                name
            )

        self.params[name] = Parameter(name, type, location, optional, default, action, append, description, warning)

    def match(self, method: str, route: str):
        match = self.pattern.fullmatch(route)
        if method == self.method and match:
            return True, match.groupdict()

        return False, None

    async def __call__(self, *args, **kwargs):
        return await self.controller(*args, **kwargs)
