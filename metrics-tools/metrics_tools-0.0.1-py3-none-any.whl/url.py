from .endpoint_base import BaseEndpoint
from .method_base import BaseMethod, MethodParams, AcceptsOrderColumn, AcceptsDateFilter, Paginatable

class Url(BaseEndpoint):
    """Url Endpoint
    
    metrics.tools url endpoint.

    Call url('https://www.example.com/') to set url.

    Methods:
        - rankings
    
    Attributes
    ----------
    endpoint : {str}
        Last part of API url
    """
    endpoint = 'url'
    
    def __init__(self, client, *args, **kwargs):
        self.rankings = Rankings(client, self.endpoint)

    def __call__(self, url):
        if len(url) > 0:
            self.rankings.params.url = url
        else:
            raise ValueError('Input can not be empty.')
        return self


class Rankings(AcceptsOrderColumn, AcceptsDateFilter, Paginatable, BaseEndpoint):
    """Rankings method
    
    metrics.tools method for url.rankings.
    Returns rankings for given url.
    
    Attributes
    ----------
    params : {MethodParams}
        Definition for fixed and needed parameters
    """

    params = MethodParams(fixed={'query':'rankings'},needed=['url'],optional=['limit','offset','order_column','order_direction'])

    def __init__(self, client, endpoint):
        super().__init__(client, endpoint)


if __name__ == '__main__':
    pass
