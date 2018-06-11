#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#

from json import JSONEncoder

from pygar.query_output import query_output


class query_json(query_output):
	_filetype = 'json'

	def out_data(self, out, filename=None):
		if self.mode == 'data':
			self._output_cache = out

		else:
			encoder = JSONEncoder()
			self._out_fd.write(encoder.encode(out))
			self._out_fd.write('\n')
