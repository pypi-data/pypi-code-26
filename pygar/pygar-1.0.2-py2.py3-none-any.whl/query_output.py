#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#

from _io import BytesIO, StringIO
from os import fdopen
from sys import version_info
from tempfile import mkstemp

from pygar.query import query


class query_output(query):
	_mode = 'data'
	_filename = None
	_out_fd = None
	_output_cache = None

	def out(self, out, filename=None):
		ret = super(query_output, self).out(out, filename)

		if not ret or self.mode != 'data':
			return ret

		return self._output_cache

	def out_open(self, filename=None):
		if self.mode == 'tmp':
			if filename is None:
				fd, filename = mkstemp(prefix='pygaR-')
				self._out_fd = fdopen(fd, 'w')
			else:
				self._out_fd = open(filename, 'w')

			self._filename = filename

		elif self.mode == 'file' and filename is not None:
			self._filename = filename

		elif self.mode == 'dump' and filename is None:
			if version_info[0] == 2:
				self._out_fd = BytesIO()
			else:
				self._out_fd = StringIO()

		elif self.mode == 'data':
			self._output_cache = []

		else:
			return False

		return True

	def out_close(self):
		if self.mode != 'data':
			if type(self._out_fd) in (BytesIO, StringIO):
				return self._out_fd.getvalue()
			else:
				self._out_fd.close()
				return '{},{}'.format(self._filetype, self._filename)
		else:
			return True

	@property
	def mode(self):
		return self._mode
	@mode.setter
	def mode(self, val):
		self._mode = val
