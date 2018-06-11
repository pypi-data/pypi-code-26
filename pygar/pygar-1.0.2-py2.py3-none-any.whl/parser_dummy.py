#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#

from pygar.parser import parser


class parser_dummy(parser):

	def _raw_readline(self):
		pass

	def open(self, path):
		pass

	def readline(self):
		pass

	def close(self):
		pass

	def get_body(self):
		pass

	def get_header(self):
		pass

	def parse_line(self):
		pass
