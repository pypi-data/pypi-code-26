

class ParamNeedDefaultValueIfItsOptional(Exception):

    pass


class ParamRedefineException(Exception):

    def __init__(self, method: str, url: str, name: str):
        self.method = method
        self.url = url
        self.name = name

    def __str__(self):
        return 'Route {} {} seems redefine param {}'.format(self.method, self.url, self.name)


class ParamComingFromUnknownLocation(Exception):

    def __init__(self, name, unexpected_location):
        self.name = name
        self.unexpected_location = unexpected_location

    def __str__(self):
        return "Parameter {} could not be loaded from location {}".format(self.name, self.unexpected_location)


class ResponseContentCouldNotFormat(Exception):

    def __str__(self):
        return "the content of rescponse could not be formatted as str"


class ParamCouldNotBeFormattedToTargetType(Exception):

    def __init__(self, target_type: str, info: str=None):
        self.target_type = target_type
        self.info = info or ''


class RouteNoMatchException(Exception):
    pass
