import datetime as dt

from licenseit.licenses.license import get_license


class New(object):
	def __init__(self, options, *args, **kwargs):
		self.options = options

	def exec(self):
		self.create_license(self.options['license'], self.options['author'], self.options['year'])
	
	def create_license(self, index, author, year):
		license = get_license(index, author, year)

		with open('LICENSE', 'w') as file:
			file.write(license)