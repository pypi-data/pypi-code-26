import typing

from apistar import http
from inspect import Parameter
from star_builder import Component

Cookie = typing.NewType('Cookie', str)


class CookieComponent(Component):

    def resolve(self,
                parameter: Parameter,
                cookie: http.Header) -> Cookie:
        name = parameter.name.replace('_', '-')
        if cookie:
            cookies = dict(c.strip().split("=", 1) for c in cookie.split(";"))
            if name in cookies:
                return Cookie(cookies[name])
