#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#

import csv, re

from pygar.query_output import query_output


class query_csv(query_output):
	_filetype = 'csv'
	_field_names = None
	_csv_fd = None

	def execute(self, regexp=True, only_first=False):
		ret = []

		if not self._qp:
			return True, 'Parser could not be initialized.'

		# successful execution, but we aren't going to parse a file
		if self._qp is True:
			ret.append([])
			return False, ret

		# parse file
		line = self._qp.readline()
		while line is not False:
			matched = True
			for field in self._filters.keys():
				try:
					fld_no = self.field_names.index(field)
				except ValueError:
					return True, 'Field not found.'

				flt = self._filters[field]

				flags = 0
				if flt['ignore_case']:
					flags = re.I

				if (
					flt['regexp'] and not re.search(
						flt['value'], line[fld_no], flags
					)
				) or (
					not flt['regexp'] and flt['value'] != line[fld_no]
				):
					matched = False

			if matched:
				if only_first:
					ret = line
					break
				else:
					ret.append(line)

			line = self._qp.readline()

		self._qp.close()
		return False, ret

	def out_data(self, out, filename=None):
		self._out_row(self.field_names)
		self._out_list(out)

	def out_open(self, filename=None):
		super(query_csv, self).out_open(filename)

		if self.mode != 'data':
			self._csv_rows = []
			self._csv_fd = csv.writer(self._out_fd, delimiter=',')

	def _out_list(self, thelist):
		for row in thelist:
			self._out_row(row)

	def _out_row(self, row):
		if len(row) == 0:
			return True

		if self.mode == 'data':
			self._output_cache.append(row)
			return True

		else:
			self._csv_rows.append(row)
			return self._csv_fd.writerow(row)

	@property
	def field_names(self):
		if self._qp and self._qp is not True:
			return self._qp.field_names
		else:
			if self._field_names is None:
				self._field_names = []

			return self._field_names
