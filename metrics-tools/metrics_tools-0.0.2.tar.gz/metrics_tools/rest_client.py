import requests
from .response import ClientResponse 

def verbosable(func):
	def wrapper(*args, **kwargs):
		if args[0].verbose:
			print('/'.join([args[0].api_url, args[1]]))
			print(args[0].params)
		return func(*args, **kwargs)
	return wrapper


class RestClient():

	api_url = 'https://metrics.tools/metricstools/api'

	def __init__(self, api_key, *args, **kwargs):
		self.verbose = kwargs.get('verbose', None)
		self.session = requests.Session()
		self.__api_key = api_key
		self.params = {}

	@property
	def params(self):
		return {**self.__params, **{'apikey':self.__api_key}}

	@params.setter
	def params(self, params):
		if isinstance(params, dict):
			params = dict((k,v) for k,v in params.items() if v is not None)
			self.__params = params
		else:
			raise TypeError('Params need to be of type dict!')


	@verbosable
	def get(self, endpoint):
		response = self.session.get('/'.join([self.api_url, endpoint]), params=self.params)
		return ClientResponse(response)


if __name__ == '__main__':
	pass