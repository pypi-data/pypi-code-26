#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#

import base64
from json import JSONDecoder, JSONEncoder

from pygar.config import DEFAULT_ENCODING
from pygar.cache import cache
from pygar.parser_form import parser_form
from pygar.query_json import query_json


class query_form(query_json):
	_parser = None

	def __init__(self, path=None):
		super(query_form, self).__init__()
		self.set_attr('path', path)

	def _map(self):
		return {}

	def _map_attr(self):
		return [('path', str)]

	def _new_query(self):
		errbool, ret = cache.get(self._attrs['path'])
		if errbool:
			return False

		self._parser = parser_form()

		# make the query input consistent, unicode/string/bytes type for attrs
		query = None
		if 'query' in self._attrs:
			query = self._attrs['query']
			if type(query) is dict:
				encoder = JSONEncoder()
				query = encoder.encode(query)
				query = query.encode(DEFAULT_ENCODING)

		# now get it into a dictionary
		if query is not None and self._parser.is_string(query):
			if query[0] != '{':
				query = query.encode(DEFAULT_ENCODING)
				query = base64.decodestring(query)
				query = query.decode(DEFAULT_ENCODING)

			decoder = JSONDecoder()
			query_dict = decoder.decode(query)
			self._attrs['query'] = query_dict

		self._parser.open(cache.full_fs_path(self._attrs['path']))
		return self._parser

	def query_headers(self):
		return self._parser.query_headers(self._attrs['query'])

	def execute(self):
		if not self._qp:
			return True, 'Query parser could not be initialized.'

		if not self._qp.body:
			return True, 'Couldn\'t parse form body [{}].'.format(
				self._attrs['path']
			)

		if 'query' in self._attrs:
			parsed_root = self._qp.parse_root(
				self._attrs['mode'], self._attrs['query'],
				header=self._attrs['header']
			)

			if not parsed_root:
				if self._attrs['header']:
					return True, 'Couldn\'t parse header structure.'
				else:
					return True, 'Couldn\'t parse XML root.'

			ret = parsed_root

		else:
			ret = {'Headers': self._qp.headers}

			doc_list = []
			for doc in self._qp.body:
				doc_list.append({
					'Type': doc.type,
					'Sequence': doc.sequence,
					'Filename': doc.filename,
					'Description': doc.description,
					'Text': '\n'.join(doc.text),
					'Text.Type': doc.text_type
				})

			ret['Body'] = doc_list

		return False, ret
