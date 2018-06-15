from functools import lru_cache, partial
from typing import List, Tuple, Type, Optional, TypeVar, Callable
from nougat.context import Request, Response
from .routing import Routing
from .route import Route
from .exceptions import *

RoutingType = TypeVar('RoutingType', bound=Routing)


class Router:

    __name__ = 'Nougat Router'

    def __init__(self) -> None:
        self.routes: List[Tuple[Type[RoutingType], 'Route']] = []

    @lru_cache(maxsize=2**5)
    def match(self, method: str, url: str) -> Optional[Tuple[Type[RoutingType], Route, dict]]:
        """
        The Routes are divided into two types: Static Route and Dynamic Route
        For Static Route, it matches provided that the url is equal to the pattern
        For Dynamic Route, it will be converted to regex pattern when and only when it was registered to Router
        There are three types of Dynamic Route:
         - Unnamed Regex type: it is allowed to write regex directly in url, but it would not be called in controller functin
         - Simple type: it is the simplest way to identify a parameter in url using `:PARAM_NAME`, it would match fully character except /
         - Named Regex type: combining Simple type and Unnamed Regex Type, writing regex and give it a name for calling
        Router will return the first matching route
        :param method:
        :param url:
        :return:
        """
        for routing, route in self.routes:
            if method == 'HEAD':
                is_match, url_dict = route.match('GET', url)
            else:
                is_match, url_dict = route.match(method, url)

            if is_match:
                return routing, route, url_dict

        raise RouteNoMatchException()

    def add(self, routing: Type[RoutingType]):
        """
        Register Routing class
        :param routing: Routing Class, not its instance
        :return:
        """
        routing_prefix = routing.prefix

        for route in routing.routes():
            route.prefix = routing_prefix
            self.routes.append((routing, route))

    async def __call__(self, app, request: 'Request', response: 'Response', next: Callable):

        try:
            # match the Routing and Route from Router
            routing_class, route, url_dict = self.match(request.method, request.url.path)
            request.url_dict = url_dict
            routing = routing_class(app, request, response, route)

            await routing.handler()

            # Formatting the Response data

        except ResponseContentCouldNotFormat:
            response.type = 'text/plain'
            response.content = "unable to format response"

        except RouteNoMatchException:
            response.code = 404
            response.type = 'text/plain'
            response.content = ''

        if request.method == 'HEAD':
            response.content = ''

        await next()



