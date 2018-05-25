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

from .domain import Domain
from .keyword import Keyword
from .url import Url
from .rest_client import RestClient

class MetricsTools():
	"""metrics.tools API
	
	Run calls for metrics.tools API

	Usage
	=====
	from metrics_tools import MetricsTools
	
	api_key = 'your api key'
	mt = MetricsTools(api_key, verbose=True)

	example_domain = mt.domain('example.com')

	visibility = example_domain.sk.get()
	rankings = example_domain.rankings.get()

	keyword_details = mt.keyword('api').details.get()

	Response examples
	=================
	example_domain.values → if values are present
	example_domain.json → parsed json response
	example_domain.result → 'success' or 'error'

	API calls
	=========
	Final API call is made through .get(), .all() or .take() if possible.
	Returns response object with attributes.
	The minimum interval for calls is 0.2 sec.
	"""

	def __init__(self, api_key, *args, **kwargs):
		self.__client = RestClient(api_key, *args, **kwargs)
		self.domain = Domain(self.__client, *args, **kwargs)
		self.keyword = Keyword(self.__client, *args, **kwargs)
		self.url = Url(self.__client, *args, **kwargs)

		

if __name__ == '__main__':
	pass