#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#


class document(object):
	_type = None
	_sequence = None
	_filename = None
	_description = None
	_text = None
	_text_type = None

	@property
	def type(self):
		return self._type
	@type.setter
	def type(self, value):
		self._type = value

	@property
	def sequence(self):
		return self._sequence
	@sequence.setter
	def sequence(self, value):
		self._sequence = value

	@property
	def filename(self):
		return self._filename
	@filename.setter
	def filename(self, value):
		self._filename = value

	@property
	def description(self):
		return self._description
	@description.setter
	def description(self, value):
		self._description = value

	@property
	def text(self):
		return self._text
	@text.setter
	def text(self, value):
		self._text = value

	@property
	def text_type(self):
		return self._text_type
	@text_type.setter
	def text_type(self, value):
		self._text_type = value

