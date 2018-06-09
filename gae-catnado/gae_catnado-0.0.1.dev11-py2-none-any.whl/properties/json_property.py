import json

from google.appengine.ext import db
import jsonschema


class JSONProperty(db.Property):
  """ A property for storing simple JSON objects backed by a schema.
  """

  data_type = db.Blob

  def __init__(self, schema=None, *args, **kwargs):
    """
    Args:
      schema: a JSON Schema per draft 3 or 4 of json-schema.org
    """
    self.schema = schema
    super(JSONProperty, self).__init__(*args, **kwargs)

  def validate(self, value):
    if self.schema:
      try:
        jsonschema.validate(value, self.schema)
      except jsonschema.ValidationError:
        print 'oh noes'
        raise db.BadValueError

  def make_value_from_datastore(self, value):
    return json.loads(value)

  def get_value_for_datastore(self, model_instance):
    value = self.__get__(model_instance, model_instance.__class__)
    return json.dumps(value)
