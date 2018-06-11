#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#

from copy import deepcopy

from pygar.cache import cache
from pygar.query_form import query_form
from pygar.query_master import query_master


class query_scrape(query_master):

	def _map_attr(self):
		ret = super(query_scrape, self)._map_attr()
		ret.extend([
			('query', str), ('mode', str), ('filename', str), ('header', bool)
		])
		return ret

	def _map_filters(self):
		if self._attrs['filename'] is not None:
			return {}
		else:
			return super(query_scrape, self)._map()

	def execute(self, regexp=True, only_first=False):
		errbool, master_ret = super(query_scrape, self).execute()
		if errbool is True:
			return True, master_ret

		# grab cache files first
		if (
			'filename' in self._attrs and
			self._attrs['filename'] is not None
		):
			errbool, ret = cache.get(self._attrs['filename'])	
		else:
			for form_row in master_ret:
				errbool, ret = cache.get(form_row[-2])
				if errbool:
					break

		# error on failure
		if errbool:
			return True, 'Could not retrieve all data files.'

		# then worry about processing them
		ret = []
		query_hdrs = None
		for form_row in master_ret:
			f = query_form()

			if (
				'filename' in self._attrs and
				self._attrs['filename'] is not None
			):
				f.set_attr('path', self._attrs['filename'])
			else:
				f.set_attr('path', form_row[-2])

			for attr in self._attrs.keys():
				f.set_attr(attr, self._attrs[attr])

			f.new_query()
			if query_hdrs is None:
				query_hdrs = f.query_headers()

			errbool, query_data = f.execute()
			if errbool is True:
				return True, query_data

			for query_row in query_data:
				new_row = deepcopy(form_row)
				for header in query_hdrs:
					found = False
					for item in query_row:
						if item[0] == header:
							new_row.append(item[1])
							found = True
							break

					if not found:
						new_row.append(None)

				ret.append(new_row)

		if query_hdrs is not None:
			self.field_names.extend(query_hdrs)

		return False, ret
