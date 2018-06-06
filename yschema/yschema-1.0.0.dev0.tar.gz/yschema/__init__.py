from .schema import Schema
from .exceptions import ValidationError, SchemaError
from .types import TYPES


__version__ = '1.0.0.dev0'


def validate(data, schema, types=None, constants=None):
    """
    Given a dictionary with data and a dictionary with a schema, either
    raise a ValidationError if the document is invalid or return without
    an error for valid data. The schema is assumed to be valid.

    You can run str() on a :class:`ValidationError` to get an
    explaination for why the data did not validate.
    """
    if not isinstance(data, dict):
        raise ValidationError('The data is not a dict, it is %s' % type(data))
    elif not isinstance(schema, dict):
        raise SchemaError('The schema is not a dict, it is %s' % type(schema))

    all_types = TYPES.copy()
    if types is not None:
        all_types.update(types)

    all_consts = {}
    if constants is not None:
        all_consts.update(constants)

    schema = Schema(schema, all_types, all_consts)
    return schema.validate(data)
