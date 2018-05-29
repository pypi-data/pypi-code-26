from .errors import ApiError

class ClientResponse():
	"""Response object
	
	Returned response object.

	Json response is parsed into response object.

	example_domain.values → if values are present
	example_domain.json → parsed json response
	example_domain.result → 'success' or 'error'
	"""

	def __init__(self, response):
		self._response = response

		if len(self._response.text) > 0:
			self.json = self._response.json()

			for attr, value in self.json.items():
				if value:
					setattr(self, attr, value)
		else:
			self._response.status_code = 204
			self.result = 'error'
			self.error_msg = 'No data'

	def __len__(self):
		return len(getattr(self, 'values', ''))

	def raise_for_status(self):
		"""Raises Exception
		
		Raises
		------
		ApiError
		"""
		if self.result == 'error':
			raise ApiError(f"Status Code: {self._response.status_code}, Error: {getattr(self, 'result', 'No error')}, Message: {getattr(self, 'error_msg', 'No message')}")
		else:
			pass

	def __repr__(self):
		return f'<metrics.tools Response [{self._response.status_code}]>'


if __name__ == '__main__':
	pass