from typing import List, Tuple, Dict, Any
from nougat import HttpException
from nougat.context import Response, Request
from .route import Route
from .utils import response_format
from .exceptions import ParamCouldNotBeFormattedToTargetType

LOCATION_MAP = {
    'url': lambda request, key: request.url_dict.get(key, None),
    'query': lambda request, key: request.url.query.get(key, None),
    'form': lambda request, key: request.form.get(key, None),
    'header': lambda request, key: request.headers.get(key, None),
    'cookie': lambda request, key: request.cookies.get(key, None)
}


class ParamDict(dict):
    def __init__(self):
        super().__init__({})

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        self[key] = value
        return value


class Routing:

    prefix: str = ''

    def __init__(self, app, request, response, route: 'Route'):
        self.request: Request = request
        self.response: Response = response
        self.route: 'Route' = route
        self.app = app

        self.params = ParamDict()

        self._origin_response_type = self.response.type
        self.response.type = None

    def redirect(self, url, forever: bool=False):
        """
        redirect to another page
        :param url: the page need to go
        :param forever: if it is forever redirect
        """
        self.response.set_header("Location", url)
        code = 301 if forever else 302
        self.abort(code)

    def abort(self, code: int, message: str = '') -> None:
        """
        abort HTTPException
        :param code: http status code
        :param message: http body
        """
        raise HttpException(code, message)

    @classmethod
    def routes(cls) -> List[Route]:
        routes: List[Route] = []
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, Route):
                routes.append(attr)

        return routes

    async def handler(self):

        await self._handler()
        self.response.type = self.response.type or self._origin_response_type

    def _params_generator(self) -> Tuple[bool, Dict[str, str]]:
        """
                format the params for resource
                """
        _parameters: Dict[str, Any] = {}
        error_dict: Dict[str, str] = {}
        for name, param_info in self.route.params.items():
            param_name = param_info.action or name

            ret = []

            # load
            for location in param_info.location:
                value_on_location = LOCATION_MAP.get(location)(self.request, name)
                if value_on_location:
                    if param_info.append:
                        if isinstance(value_on_location, list):
                            ret.extend(value_on_location)
                        else:
                            ret.append(value_on_location)
                    else:
                        if isinstance(value_on_location, list):
                            ret.append(value_on_location[0])
                        else:
                            ret.append(value_on_location)

            # set default value if optional is True and ret is empty
            if not ret:
                if param_info.optional:
                    ret = [param_info.default]
                else:
                    error_dict[name] = param_info.warning or 'miss parameter'
                    continue

            if not param_info.append:
                ret = [ret[0]]

            # verify the type of parameter
            try:

                ret = list(map(param_info.type, ret))
            except ParamCouldNotBeFormattedToTargetType as e:
                error_dict[name] = e.info

            except ValueError:
                error_dict[name] = 'cannot be converted to {}'.format(param_info.type.__name__)

            _parameters[param_name] = (ret if param_info.append else ret[0])

        if not error_dict:

            for key, value in _parameters.items():
                self.params.__setattr__(key, value)

            return True, error_dict
        return False, error_dict

    async def _handler(self):

        ret = await self.route(self)
        self.response.content = ret or ''


class RestRouting(Routing):

    async def _handler(self):
        is_pass, error_dict = self._params_generator()
        if not is_pass:
            response_type, result = response_format(error_dict)
            self.response.code = 400
            self.response.type = response_type
            self.response.content = result

        else:
            ret = await self.route(self)
            if isinstance(ret, tuple) and len(ret) == 2 and isinstance(ret[1], int):
                self.response.code = ret[1]
                ret = ret[0]
            response_type, result = response_format(ret)
            if not self.response.type:
                self.response.type = response_type
            self.response.content = result
