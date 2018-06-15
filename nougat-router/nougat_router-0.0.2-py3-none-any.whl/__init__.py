from .exceptions import *
from .param import Parameter, ParameterGroup
from .route import Route
from .router import Router
from .routing import Routing, RestRouting

from typing import Callable, Any, List, Union


def __method_generator(method: str, url: str) -> Callable:

    def decorator(controller: Union[Callable, Route]) -> 'Route':

            if isinstance(controller, Route):
                controller.method = method
                controller.url = url
                return controller
            else:
                return Route(method, url, controller)

    return decorator


def get(route: str) -> Callable:

    return __method_generator('GET', route)


def post(route: str) -> Callable:

    return __method_generator('POST', route)


def patch(route: str) -> Callable:

    return __method_generator('PATCH', route)


def put(route: str) -> Callable:

    return __method_generator('PUT', route)


def delete(route: str) -> Callable:

    return __method_generator('DELETE', route)


def param(name: str,
          type: Callable[[str], Any],
          location: (str, List[str]) = 'query',
          optional: bool = False,
          default: Any = None,
          action=None,
          append=False,
          description: str = None,
          warning: str = None
          ) -> Callable:

    def decorator(controller: Union[Callable, Route]) -> Route:

        if not isinstance(controller, Route):
            controller = Route('', None, controller)

        controller.add_param(name, type,  location, optional, default, action, append, description, warning)

        return controller

    return decorator


def params(group: 'ParameterGroup') -> Callable:

    def decorator(controller: Union[Callable, Route]):
        if not isinstance(controller, Route):
            controller = Route('', None, controller)

        for attr_name in dir(group):
            attr = getattr(group, attr_name)
            if isinstance(attr, Parameter):
                controller.add_param(attr_name, attr.type, attr.location, attr.optional, attr.default, attr.action, attr.append, attr.description)

        return controller

    return decorator
