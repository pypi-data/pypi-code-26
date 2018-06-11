#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#


from pygar.parser import parser


class parser_index(parser):

	def get_header(self):
		ret = []
		date = None
		phase = 1
		line = self._raw_readline()

		while line is not False:
			line = line.strip()
			if line[0:19] == 'Last Data Received:':
				date = line[23:]

			elif phase == 1 and line == '':
				# empty padding
				phase = 2

			elif phase == 2 and line != '':
				ret.append(line)

				# read two lines for header and move on to
				# reading data
				self.field_names = self.parse_line(line)

				# trash extra "---" row
				ret.append(self._raw_readline())
				break

			ret.append(line)
			line = self._raw_readline()

		return '\n'.join(ret)

	def get_body(self):
		pass


class parser_index_sep(parser_index):
	_separator = None

	def __init__(self, separator=','):
		super(parser_index_sep, self).__init__()
		self._separator = separator

	def parse_line(self, line):
		return line.strip().split(self._separator)
