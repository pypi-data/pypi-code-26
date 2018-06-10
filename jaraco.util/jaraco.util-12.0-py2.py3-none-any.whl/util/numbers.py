from __future__ import unicode_literals, absolute_import


import json
import numbers

import contextlib2


def coerce(value):
	"""
	coerce takes a value and attempts to convert it to a float,
	or int.

	If none of the conversions are successful, the original value is
	returned.

	>>> coerce('3')
	3

	>>> coerce('3.0')
	3.0

	>>> coerce('foo')
	'foo'

	>>> coerce({})
	{}

	>>> coerce('{}')
	'{}'
	"""
	with contextlib2.suppress(Exception):
		loaded = json.loads(value)
		assert isinstance(loaded, numbers.Number)
		return loaded
	return value
