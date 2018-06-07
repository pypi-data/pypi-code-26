from .schema import Schema
from .exceptions import ValidationError, SchemaError
from .types import TYPES


__version__ = '1.0.1'


def validate(data, schema, types=None, constants=None, return_errors=False):
    """
    Given a dictionary with data and a dictionary with a schema, either
    raise a ValidationError if the document is invalid or return without
    an error for valid data. The schema is assumed to be valid.

    You can run str() on a :class:`ValidationError` to get an
    explaination for why the data did not validate. If return_errors
    is True then the validation will return a list of error messages
    instead of raising an exception. Schema errors will still raise.
    """
    def raise_error(message):
        if return_errors:
            return [message]
        else:
            raise ValidationError(message)

    if not isinstance(data, dict):
        raise_error('The data is not a dict, it is %s' % type(data))
    elif not isinstance(schema, dict):
        raise_error('The schema is not a dict, it is %s' % type(schema))

    all_types = TYPES.copy()
    if types is not None:
        all_types.update(types)

    all_consts = {}
    if constants is not None:
        all_consts.update(constants)

    schema = Schema(schema, all_types, all_consts)
    errors = schema.validate(data)

    if return_errors:
        return errors
    elif errors:
        raise ValidationError('\n'.join(errors))
