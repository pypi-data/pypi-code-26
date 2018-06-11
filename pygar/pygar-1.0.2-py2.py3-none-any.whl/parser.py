#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#

import gzip

from pygar.config import DEFAULT_ENCODING


class parser(object):
	_field_names = None
	_fp = None
	_header = None
	_body = None
	_path = None

	def __init__(self):
		pass

	def __del__(self):
		self.close()

	def _raw_readline(self):
		if self._fp is None:
			return False

		line = self._fp.readline()
		line = line.decode(DEFAULT_ENCODING)

		# must have newline at end to be considered
		if len(line.strip()) == 0 and line[-1:] != '\n':
			self.close()
			return False

		return line[0:-1]

	def open(self, path):
		self._path = path

		if path[-3:] == ".gz":
			self._fp = gzip.open(path)
		else:
			self._fp = open(path, "rb")

		# start by grabbing headers
		self._header = self.get_header()

		# grab body
		self._body = self.get_body()

		return self._header

	def readline(self):
		line = self._raw_readline()
		if not line:
			return False
		else:
			ret = self.parse_line(line)
			return ret

	def close(self):
		if self._fp is None:
			return

		self._fp.close()
		self._fp = None

	def get_body(self):
		pass

	def get_header(self):
		pass

	def parse_line(self, line):
		pass

	@property
	def field_names(self):
		return self._field_names
	@field_names.setter
	def field_names(self, value):
		self._field_names = value

	@property
	def headers(self):
		return self._headers
	@headers.setter
	def headers(self, value):
		self._headers = value

	@property
	def body(self):
		return self._body
	@body.setter
	def body(self, value):
		self._body = value
