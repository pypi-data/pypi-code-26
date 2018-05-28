import apache_beam as beam


# Performs one transform... then passes the collection through to another.
class Reemitter(beam.PTransform): # pylint: disable=no-member,too-few-public-methods

  def __init__(self, transform):

    self.transform = transform

  def expand(self, collection):
    (collection | self.transform) # pylint: disable=pointless-statement
    return collection

    import apache_beam as beam


def create_tupler(key):
  """Sane as `create_keyed_tuple`, but returns a function that takes the
  record to be converted."""

  if isinstance(key, basestring):
    def tupler(record):
      return (record[key], record)

  if callable(key):
    def tupler(record):
      return (key(record), record)

  return tupler


class Dedupe(beam.PTransform):
  """Given a key creator function, or a dict key name, this will create a
  dedupe transform... it's exposed as a `Ptransform so that it can act as a single
  step in a larger pipeline.`"""
  def __init__(self, key):
    super(self.__class__, self).__init__()
    self.tupler = create_tupler(key)
    self.untupler = lambda v: v[-1]

  def expand(self, collection):
    return (
        collection
        | beam.Map(self.tupler)
        | beam.GroupByKey()
        | beam.Map(self.untupler)
    )

