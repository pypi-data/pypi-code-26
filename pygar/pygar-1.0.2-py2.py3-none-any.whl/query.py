#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#

import re


class query(object):
	_attrs = None
	_out_fd = None
	_filters = None
	_headers = None
	_mappings = None
	_qp = None

	def __init__(self):
		self._attrs = {}
		self._filters = {}
		self._mappings = self._map()

	def add_filter(self, field, value, regexp=False, ignore_case=False):
		self._filters[field] = {
			'field': field,
			'value': value,
			'regexp': regexp,
			'ignore_case': ignore_case
		}

	def by(self, field, value):
		if field in self._mappings.keys():
			field = self._mappings[field]

		regexp = False
		ignore_case = False

		if type(value) not in (dict, bool):
			match = re.match("^([/@])(.*)\\1([i]?)$", str(value))
			if match:
				regexp = True
				value = match.group(2)
				if match.group(3) == 'i':
					ignore_case = True

		return self.add_filter(field, value, regexp, ignore_case)

	def set_attr(self, attr, value):
		if (
			value is not None and type(value) is not bool
			and type(value) is not dict
		):
			value = str(value)
		self._attrs[attr] = value

	def has_attr(self, attr):
		attrs = self._map_attr()
		for an_attr,val in attrs:
			if an_attr == attr:
				return True
	
		return False

	def get_attrs(self):
		return self._attrs

	def new_query(self):
		self._qp = self._new_query()
		return bool(self._qp)

	def out(self, out, filename=None):
		self.out_open(filename)
		self.out_data(out, filename)
		return self.out_close()

	def _map_filters(self):
		return self._map()

	@property
	def filters(self):
		return self._filters
	@filters.setter
	def filters(self, value):
		self._filters = value

	@property
	def field_names(self):
		return self._qp.field_names

	def _map_attr(self):
		pass
	def _map(self):
		pass
	def _new_query(self):
		pass
	def execute(self):
		pass
	def out_data(self, out, filename=None):
		pass
	def out_open(self, filename=None):
		pass
	def out_close(self):
		pass
