
def sequence(*funcs):
  """A simple function sequence utility."""
  def sequenced(value):
    for func in iter(funcs):
      value = func(value)
    return value

  return sequenced


def compose(*funcs):
  """Compose functions right to left"""
  rev = funcs[::-1]
  return sequence(*rev)


def create_keyed_tuple(record, key):
  """Converts records to keyed tuples `(derived_key, original_record)`
  to be used for grouping transformations that required a tuple in that format
  """

  # The key is a string - grab the value from the object.
  if isinstance(key, basestring):
    if not isinstance(record, dict):
      raise TypeError('To use a string key the records must be dictionaries.')

    value = record[key]
    return (value, record)

  # The key is a function - pass it the object, returns value is the tuple key.
  if callable(key):
    value = key(record)
    return (value, record)

  # TODO: Make this a little more verbose.
  raise TypeError('Expected second argument to be a string or function.')


def create_tupler(key):
  """Similar to `create_keyed_tuple`, but returns a function that takes the
  record to be converted, which should then be passed each record.

  This is mostly useful for creating joinable values.
  """

  if isinstance(key, basestring):
    def tupler(record):
      return (record[key], record)

  if callable(key):
    def tupler(record): # pylint: disable=function-redefined
      return (key(record), record)

  return tupler


def untuple_keyed_value(value):
  """A trivial util to to reverse the tupling above... takes a value that looks
  like; `(key, record)`, and returns `record` """
  return value[-1]
