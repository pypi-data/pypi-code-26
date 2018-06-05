""" See http://googleappengine.blogspot.com/2009/07/writing-custom-property-classes.html
"""

import decimal

from google.appengine.ext import db


class DecimalProperty(db.Property):
  """ Property for storing Decimal types.
  """

  data_type = decimal.Decimal

  def get_value_for_datastore(self, model_instance):
    return str(super(DecimalProperty, self).get_value_for_datastore(model_instance))

  def make_value_from_datastore(self, value):
    return decimal.Decimal(value)

  def validate(self, value):
    value = super(DecimalProperty, self).validate(value)
    if value is None or isinstance(value, decimal.Decimal):
      return value
    elif isinstance(value, basestring):
      return decimal.Decimal(value)
    raise db.BadValueError("Property %s must be a Decimal or string." % self.name)
