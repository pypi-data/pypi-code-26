#       _                         __    __           __   __      __         __
#      (_)___  ____  ____  __  __/ /_  / /___ ______/ /__/ /___ _/ /_  ___  / /
#     / / __ \/ __ \/ __ \/ / / / __ \/ / __ `/ ___/ //_/ / __ `/ __ \/ _ \/ / 
#    / / /_/ / / / / / / / /_/ / /_/ / / /_/ / /__/ ,< / / /_/ / /_/ /  __/ /  
# __/ /\____/_/ /_/_/ /_/\__, /_.___/_/\__,_/\___/_/|_/_/\__,_/_.___/\___/_/   
#/___/                  /____/                                                 
#
#
# author: Johannes Kunze
# web: http://www.jonnyblacklabel.de/
# twitter: @jonnyblacklabel
#

from .endpoint_base import BaseEndpoint
from .method_base import BaseMethod, MethodParams, AcceptsKeywordFilter, AcceptsDateFilter

class Keyword(BaseEndpoint):
	"""Keyword Endpoint
	
	metrics.tools keyword endpoint.

	Call keyword('example') to set keyword.

	Methods:
		- details
		- related
	
	Attributes
	----------
	endpoint : {str}
		Last part of API url
	"""
	endpoint = 'keyword'
	
	def __init__(self, client, *args, **kwargs):
		self.details = Details(client, self.endpoint)
		self.related = Related(client, self.endpoint)

	def __call__(self, keyword):
		if len(keyword) > 0:
			self.details.params.keyword = keyword
			self.related.params.keyword = keyword
		else:
			raise ValueError('Input can not be empty.')
		return self


class Details(BaseMethod):
    """Details Method
    
    metrics.tools method for keyword.details.
    Returns searchvolume, cpc and competition for given keyword.
    
    Attributes
    ----------
    params : {MethodParams}
        Definition for fixed and needed parameters
    """

    params = MethodParams(fixed={'query':'details'},needed=['keyword'])

    def __init__(self, client, endpoint):
        super().__init__(client, endpoint)


class Related(BaseMethod):
    """Related Method
    
    metrics.tools method for keyword.related.
    Returns related keyword for given keyword.
    
    Attributes
    ----------
    params : {MethodParams}
        Definition for fixed and needed parameters
    """

    params = MethodParams(fixed={'query':'related'},needed=['keyword'],optional=['details'])

    def __init__(self, client, endpoint):
        super().__init__(client, endpoint)

    def details(self, degree):
        """Set detail degree
        
        Set the detail degree for related keywords.
        Represents the "schnell-umfassend" controle in the frontend.
        
        Parameters
        ----------
        degree : {string}
            Filter by degree, default: 3, min 0 max 3
        
        Returns
        -------
        self
        """
        self.params.details = degree
        return self

if __name__ == '__main__':
	pass