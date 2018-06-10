

class ValidationError(Exception):
  """Raise when a request validation decorator fails.

  See: validate.
  """

  pass


def validate(key, types, extra_validators=None, required=False):
  """Use as a decorator to validate incoming request data.

  Args:
    key: the request data key to validate
    types: a type or list or list of types that are acceptable
    extra_validators: an optional function or list of functions to call on the
      specified key
    required: optional bool; whether this field is required (defaults False)

  Raises:
    AssertionError: if types is not a type or list of types
    ValidationError: if the request contains invalid data
  """
  def outer_decorator(func):
    def inner_decorator(self, *args, **kwargs):

      assert isinstance(types, (list, type))

      value = self.request.get(key)

      if not value and required:
        raise ValidationError('{} is required but missing'.format(key))

      if not isinstance(value, types):
        found = type(value)
        raise ValidationError('Expected type {}, got {}'.format(types, found))

      if extra_validators:

        # convert single-function arguments to a list. since onecannot assign to
        # a variable defined in an enclosing scope and then reference it later
        # in the same function without raising an UnboundLocalError, give the
        # list a different name
        if not isinstance(extra_validators):
          validators_to_run = [extra_validators]
        else:
          assert isinstance(extra_validators, list)
          validators_to_run = extra_validators

        for extra_validator in validators_to_run:
          extra_validator(value)

      func(self, *args, **kwargs)

    return inner_decorator
  return outer_decorator
