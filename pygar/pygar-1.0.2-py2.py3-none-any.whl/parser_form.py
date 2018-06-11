#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#

from xml.etree import ElementTree
from sys import version_info

from pygar.document import document
from pygar.parser import parser


class parser_form(parser):
	def __init__(self):
		super(parser_form, self).__init__()

	def _parse_tag_header(self, header_raw):
		ret = []

		line = header_raw.pop(0)
		while line is not False:
			if line.strip() == '':
				line = header_raw.pop(0)
				continue

			if len(line.split('>')) == 1:
				header_raw.insert(0, line)
				break

			line_split = line[1:].split('>')

			if len(line_split) != 2:
				line = header_raw.pop(0)
				continue

			tag,val = line_split
			tag = '.'.join([word.capitalize() for word in tag.split('-')])

			ret.append((tag,val))
			line = header_raw.pop(0)

		return ret, header_raw

	def _parse_header(self, lines, tabstop=0):
		if len(lines) == 0:
			return {}, 0

		obj = {}
		prev_attr = None
		i = 0

		while len(lines) > i and (
			tabstop == 0 or (
				tabstop > 0 and
				tabstop*'\t' == lines[i][0:tabstop]
			)
		):
			if lines[i][tabstop] == '\t':
				obj[prev_attr], parsed_lines = \
					self._parse_header(lines[i:], tabstop+1)

				i += parsed_lines

			else:
				splitret = lines[i].split(':')
				if len(splitret) != 2:
					i += 1
					continue

				attr,val = splitret
				attr = attr.strip().replace('-', ' ')
				attr = '.'.join([word.capitalize() for word in attr.split(' ')])
				val = val.strip()

				obj[attr] = val
				prev_attr = attr

				i += 1

		return obj, i

	def get_header(self):
		header_raw = []

		line = self._raw_readline()
		while line is not False:
			if line != '':
				if line.upper() == '</SEC-HEADER>':
					break
				header_raw.append(line)

			line = self._raw_readline()

		headers_tag, header_remaining = self._parse_tag_header(header_raw)
		self._headers, parsed_lines = self._parse_header(header_remaining)

		for tag,val in headers_tag:
			self._headers[tag] = val

		return self._headers

	def get_body(self):
		docs = []
		doc_lines = []
		doc_started = False
		line = self._raw_readline()
		while line is not False:
			if not doc_started:
				if line.upper() == '<DOCUMENT>':
					doc_started = True

			else:
				if line.upper() == '</DOCUMENT>':
					new_doc = document()

					text_lines = []
					in_header = True
					type_set = False
					for doc_line in doc_lines:
						if in_header:
							if doc_line[0:6].upper() == '<TEXT>':
								in_header = False
							elif doc_line[0:6].upper() == '<TYPE>':
								new_doc.type = doc_line[6:]
							elif doc_line[0:10].upper() == '<SEQUENCE>':
								new_doc.sequence = doc_line[10:]
							elif doc_line[0:10].upper() == '<FILENAME>':
								new_doc.filename = doc_line[10:]
							elif doc_line[0:13].upper() == '<DESCRIPTION>':
								new_doc.description = doc_line[13:]
						else:
							if (
								doc_line[0:7].upper() == '</TEXT>' or
								doc_line[0:6].upper() == '</PDF>' or
								doc_line[0:6].upper() == '</XML>' or
								doc_line[0:6].upper() == '</XBRL>'
							):
								break

							if not type_set:
								if doc_line[0:5].upper() == '<PDF>':
									new_doc.text_type = 'pdf'
									type_set = True
									continue

								elif doc_line[0:5].upper() == '<XML>':
									new_doc.text_type = 'xml'
									type_set = True
									continue

								elif doc_line[0:5].upper() == '<XBRL>':
									new_doc.text_type = 'xbrl'
									type_set = True
									continue

								elif (
									doc_line[0:6].upper() == '<HTML>' or
									doc_line[0:9].upper() == '<!DOCTYPE'
								):
									new_doc.text_type = 'html'

								elif new_doc.type.upper() == 'GRAPHIC':
									new_doc.text_Type = 'graphic'

								else:
									new_doc.text_type = 'other'

								type_set = True

							text_lines.append(doc_line)

					new_doc.text = text_lines

					doc_lines = []
					docs.append(new_doc)

				else:
					doc_lines.append(line)

			line = self._raw_readline()

		if docs == []:
			return False
		else:
			return docs

	def _parse_xml(self, elem=None, root=False):
		ret = {}

		if type(self._body) is not list:
			return False

		xml_doc = None
		for doc in self._body:
			if doc.text_type == 'xml':
				xml_doc = doc
				break

		if xml_doc is None:
			return False

		body = xml_doc.text

		if elem is None:
			elem = ElementTree.fromstring('\n'.join(body))

		# base case
		if root:
			ret[elem.tag] = self._parse_xml(elem)
			return ret

		for sub_elem in elem:
			new_elem_ret = self._parse_xml(sub_elem)
			if sub_elem.tag in ret:
				if type(ret[sub_elem.tag]) is not list:
					ret[sub_elem.tag] = [ret[sub_elem.tag]]
				ret[sub_elem.tag].append(new_elem_ret)

			else:
				ret[sub_elem.tag] = new_elem_ret

		if ret == {}:
			ret = elem.text

		return ret

	@staticmethod
	def _is_numeric(strcmp):
		strcmp = strcmp.replace('.', '', 1)
		return strcmp.isdigit()

	def _mode_query_prune_perform(self, root, query):
		all_conditions_passed = True

		for elem in query:
			if elem == '_eq':
				if root != query[elem]:
					all_conditions_passed = False
					break

			elif elem == '_lt':
				if (
					not self._is_numeric(root) or
					not self._is_numeric(query[elem]) or
					root < query[elem]
				):
					all_conditions_passed = False
					break

			elif elem == '_gt':
				if (
					not self._is_numeric(root) or
					not self._is_numeric(query[elem]) or
					root > query[elem]
				):
					all_conditions_passed = False
					break

			elif elem == '_le':
				if (
					not self._is_numeric(root) or
					not self._is_numeric(query[elem]) or
					root <= query[elem]
				):
					all_conditions_passed = False
					break

			elif elem == '_ge':
				if (
					not self._is_numeric(root) or
					not self._is_numeric(query[elem]) or
					root >= query[elem]
				):
					all_conditions_passed = False
					break

			elif elem == '_z':
				if root != '' and root is not None:
					all_conditions_passed = False
					break

			elif elem == '_n':
				if root == '' and root is not None:
					all_conditions_passed = False
					break

			elif elem not in root:
				all_conditions_passed = False
				break

			else:
				ret = self._mode_query_prune_perform(root[elem], query[elem])
				if ret == {}:
					all_conditions_passed = False

		if all_conditions_passed:
			return root
		else:
			return {}

	def _mode_query_prune_search_item(self, root, query):
		if elem != '_prune' and elem in root:
			prev = root[elem]
			root[elem] = self._mode_query_prune_search(
				root[elem], query[elem]
			)

	def _mode_query_prune_search(self, root, query):
		if '_prune' in query:
			root = self._mode_query_prune_perform(root, query['_prune'])

		if type(query) is dict and type(root) is dict:
			for elem in query:
				if elem != '_prune' and elem in root:
					if type(root[elem]) is not list:
						root[elem] = self._mode_query_prune_search(
							root[elem], query[elem]
						)
					else:
						new_list = []
						for item in root[elem]:
							new_item = self._mode_query_prune_search(
								item, query[elem]
							)

							if new_item != {}:
								new_list.append(new_item)

						if len(new_list) == 1:
							new_list = new_list[0]
						elif len(new_list) == 0:
							new_list = None

						root[elem] = new_list

		return root

	def is_string(self, val):
		if version_info[0] == 2:
			return type(val) is str or type(val) is unicode
		else:
			return type(val) is str

	def _mode_query_retrieve(self, root, query):
		ret = []

		for elem in query:
			if elem == '_prune':
				continue

			if elem in root:
				if (
					type(root[elem]) in (dict, list) and
					type(query[elem]) is dict
				):
					if type(root[elem]) is list:
						vals = []
						for item in root[elem]:
							vals.append(self._mode_query_retrieve(
								item, query[elem]
							))

						ret.append(vals)

					else:
						ret.extend(self._mode_query_retrieve(
							root[elem], query[elem]
						))

				elif (
					(
						type(root[elem]) is list or
						self.is_string(root[elem])
					) and self.is_string(query[elem])
				):
					if type(root[elem]) is list:
						vals = []
						for item in root[elem]:
							vals.append([(query[elem], item)])

						ret.append(vals)

					else:
						ret.append((query[elem], root[elem]))

		return ret

	@staticmethod
	def _list_combine(list1, list2):
		ret = []

		if len(list1) > len(list2):
			bigger_list = list1
			smaller_list = list2
		else:
			bigger_list = list2
			smaller_list = list1

		for item in bigger_list:
			for s_item in smaller_list:
				if type(item) is list:
					ret.append(item + [s_item])
				else:
					ret.append([item, s_item])

		return ret

	def _list_expand(self, thelist):
		tuples = []
		lists = []

		for item in thelist:
			if type(item) == tuple:
				tuples.append(item)
			elif type(item) == list:
				lists.append(item)

		tuples = [tuples]
		if len(lists) == 0:
			return tuples

		for thelist in lists:
			tuples = self._list_combine(tuples, thelist)

		# flatten now
		ret = []
		for thelist in tuples:
			newlist = []
			for item in thelist:
				if type(item) is tuple:
					newlist.append(item)
				else:
					newlist.extend(item)
			ret.append(newlist)

		return ret

	def query_headers(self, query):
		ret = []
		for item in query:
			if item == '_prune':
				continue
			elif self.is_string(query[item]):
				ret.append(query[item])
			elif type(query[item]) is dict:
				ret.extend(self.query_headers(query[item]))

		ret.sort()
		uniq_ret = []
		last = None
		for item in ret:
			if item != last:
				uniq_ret.append(item)
			last = item

		return uniq_ret

	def _mode_query(self, root, query):
		pruned_root = self._mode_query_prune_search(root, query)
		retrieved_data = self._mode_query_retrieve(pruned_root, query)
		retrieved_data = self._list_expand(retrieved_data)
		return retrieved_data

	def parse_root(self,
		mode, query=None, header=False
	):
		if not header:
			root = self._parse_xml(root=True)
		else:
			root = self._header

		if root is False:
			return False

		if (mode == 'query' or mode is None) and query is not None:
			ret = self._mode_query(root, query)

		else:
			ret = None

		return ret

	def parse_line(self, line):
		return line.rstrip()
