from .endpoint_base import BaseEndpoint
from .method_base import BaseMethod, MethodParams, AcceptsOrderColumn, AcceptsDateFilter, AcceptsKeywordFilter, Paginatable

class Domain(BaseEndpoint):
	"""Domain Endpoint
	
	metrics.tools domain endpoint.

	Call domain('example.com') to set domain.

	Methods:
		- sk [visibility]
		- rankings
		- position
	
	Attributes
	----------
	endpoint : {str}
		Last part of API url
	"""
	endpoint = 'domain'
	
	def __init__(self, client, *args, **kwargs):
		self.sk = Sk(client, self.endpoint)
		self.rankings = Rankings(client, self.endpoint)
		self.position = Position(client, self.endpoint)

	def __call__(self, domain):
		if len(domain) > 0:
			self.sk.params.domain = domain
			self.rankings.params.domain = domain
			self.position.params.domain = domain
		else:
			raise ValueError('Input can not be empty.')
		return self


class Sk(AcceptsDateFilter, BaseMethod):
    """Visibility Method
    
    metrics.tools method for domain.sk.
    Returns the visibility for given domain.
    
    Attributes
    ----------
    params : {MethodParams}
        Definition for fixed, needed and optional parameters
    """

    params = MethodParams(fixed={'query':'sk'},needed=['domain'],optional=['type','date'])
     
    def __init__(self, client, endpoint):
        super().__init__(client, endpoint)

    def current(self):
        """Current visibility
        
        Filters API call for latest visibility score
        
        Returns
        -------
        self
        """
        self.params.type = 'current'
        return self

    def all(self):
        """Get all
        
        Run API call for all visibility values
        
        Returns
        -------
        ClientResponse
            metrics.tools response object
        """
        self.params.type = 'all'
        return self.get()

    def minmax(self):
        """Set minmax
        
        Filter API call for min and max historical visibility value
        
        Returns
        -------
        self
        """
        self.params.type = 'minmax'
        return self


class Rankings(AcceptsOrderColumn, AcceptsDateFilter, Paginatable):
    """Rankings Method
    
    metrics.tools method for domain.rankings.
    Returns rankings for given domain.
    
    Attributes
    ----------
    params : {MethodParams}
        Definition for fixed, needed and optional parameters
    """

    params = MethodParams(fixed={'query':'rankings'},needed=['domain'],optional=['limit','offset','order_column','order_direction'])

    def __init__(self, client, endpoint):
        super().__init__(client, endpoint)


class Position(AcceptsKeywordFilter, AcceptsDateFilter, BaseMethod):
    """Position Method
    
    metrics.tools method for domain.position.
    Returns ranking position for given domain for given keyword.
    
    Attributes
    ----------
    params : {MethodParams}
        Definition for fixed, needed and optional parameters
    """

    params = MethodParams(fixed={'query':'position'},needed=['domain','keyword'],optional=['date'])

    def __init__(self, client, endpoint):
        super().__init__(client, endpoint)

if __name__ == '__main__':
	pass