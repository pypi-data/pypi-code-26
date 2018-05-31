from st_library.utils.api_client import resource
from st_library.utils.api_client import request


class ApiClient(object):
    def __init__(self):
        raise TypeError('This class should not be initialized')

    res = resource

    @staticmethod
    def get(*args, **kwargs):
        return request.get(*args, **kwargs)

    @staticmethod
    def post(*args, **kwargs):
        return request.post(*args, **kwargs)

    @staticmethod
    def delete(*args, **kwargs):
        return request.delete(*args, **kwargs)
