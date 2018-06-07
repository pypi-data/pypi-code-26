"""
YSchema Types that are used when validating

All built in validation types except (sub) schema and alias are defined
below. The built in types are registered in the TYPES dictionary. Any
type used in a schema must be either defined in TYPES, defined as an
alias in the schema, or a user provided type given when parsing the
schema.

A Type is an object that implements a validate() method that takes value
and key name and returns a list of error messages (an empty list for valid
data). Only the value is typically validated, the key is used to construct
error messages.
"""
import inspect


PINF = float('+inf')
MINF = float('-inf')
TYPES = {}


def register_schema_type(name):
    """
    A class decorator to register YSchema types
    """
    def register(schema_type_class):
        TYPES[name] = schema_type_class
        schema_type_class.type_name = name
        return schema_type_class
    return register


def get_type_object(candidate):
    """
    To allow users to specify things like ``any_of(types=(str, float))``
    or ``any_of(types=(str(min_len=4), float))``, this function checks
    for instance or class and instantiates if necessary
    """
    if inspect.isclass(candidate):
        candidate = candidate()
    return candidate


class BaseType:
    def __repr__(self):
        return '<SchemaType %s>' % self.type_name


@register_schema_type('Any')
class AnyType(BaseType):
    def validate(self, value, key):
        return []


@register_schema_type('bool')
class BoolType(BaseType):
    def __init__(self, equals=None):
        self.equals = equals

    def validate(self, value, key):
        if not isinstance(value, bool):
            return ['Expected a boolean for key %r, got %r which'
                    ' is a %s' % (key, value, type(value))]

        errors = []
        if self.equals is not None:
            if value != self.equals:
                errors.append('Expected %r == %r, got %r' %
                              (key, self.equals, value))
        return errors


@register_schema_type('str')
class StringType(BaseType):
    def __init__(self, min_len=0, max_len=1e100, equals=None, prefix=None):
        self.min_len = min_len
        self.max_len = max_len
        self.equals = equals
        self.prefix = prefix

    def validate(self, value, key):
        if not isinstance(value, str):
            return ['Expected a string for key %r, got %r which '
                    'is a %s' % (key, value, type(value))]

        errors = []
        if len(value) < self.min_len:
            errors.append('Expected a string of length at least %r for'
                          ' %r, got %r which has length %r' %
                          (self.min_len, key, value, len(value)))

        if len(value) > self.max_len:
            errors.append('Expected a string of length at most %r for'
                          ' %r, got %r which has length %r' %
                          (self.max_len, key, value, len(value)))

        if isinstance(self.equals, str):
            if value != self.equals:
                errors.append('Expected %r = %r, got %r' %
                              (key, self.equals, value))
        elif self.equals is not None:
            if value not in self.equals:
                errors.append('Expected %r in %r, got %r' %
                              (key, self.equals, value))

        if self.prefix is not None:
            if not value.startswith(self.prefix):
                errors.append('Expected %r starting with %r, got %r' %
                              (key, self.prefix, value))
        return errors


@register_schema_type('int')
class IntType(BaseType):
    def __init__(self, min_val=MINF, max_val=PINF, equals=None):
        self.min_val = min_val
        self.max_val = max_val
        self.equals = equals

    def validate(self, value, key):
        if not isinstance(value, int):
            return ['Expected an integer for key %r, got %r which'
                    ' is a %s' % (key, value, type(value))]

        errors = []
        if value < self.min_val:
            errors.append('Expected an integer larger than %r for '
                          '%r, got %r' % (self.min_val, key, value))

        if value > self.max_val:
            errors.append('Expected an integer smaller than %r for '
                          '%r, got %r' % (self.max_val, key, value))

        if isinstance(self.equals, int):
            if value != self.equals:
                errors.append('Expected %r = %r, got %r' %
                              (key, self.equals, value))
        elif self.equals is not None:
            if value not in self.equals:
                errors.append('Expected %r in %r, got %r' %
                              (key, self.equals, value))
        return errors


@register_schema_type('float')
class FloatType(BaseType):
    def __init__(self, min_val=MINF, max_val=PINF, equals=None):
        self.min_val = min_val
        self.max_val = max_val
        self.equals = equals

    def validate(self, value, key):
        num = (float, int)
        if not isinstance(value, num):
            return ['Expected a float for key %r, got %r which'
                    ' is a %s' % (key, value, type(value))]

        errors = []
        if value < self.min_val:
            errors.append('Expected a float larger than %r for '
                          '%r, got %r' % (self.min_val, key, value))

        if value > self.max_val:
            errors.append('Expected a float smaller than %r for '
                          '%r, got %r' % (self.max_val, key, value))

        if isinstance(self.equals, num):
            if value != self.equals:
                errors.append('Expected %r = %r, got %r' %
                              (key, self.equals, value))
        elif self.equals is not None:
            if value not in self.equals:
                errors.append('Expected %r in %r, got %r' %
                              (key, self.equals, value))
        return errors


@register_schema_type('list')
class ListType(BaseType):
    def __init__(self, type=None, min_len=0, max_len=1e100):
        self.item_type = type
        self.min_len = min_len
        self.max_len = max_len

    def validate(self, value, key):
        if not isinstance(value, list):
            return ['Expected a list for key %r, got %r which '
                    'is a %s' % (key, value, type(value))]

        errors = []
        if len(value) < self.min_len:
            errors.append('Expected a list of length at least %r for'
                          ' %r, got %r which has length %r' %
                          (self.min_len, key, value, len(value)))

        if len(value) > self.max_len:
            errors.append('Expected a list of length at most %r for'
                          ' %r, got %r which has length %r' %
                          (self.max_len, key, value, len(value)))

        if self.item_type is not None:
            required_type = get_type_object(self.item_type)
            for i, item in enumerate(value):
                errors.extend(required_type.validate(item, '%s[%d]' % (key, i)))
        return errors


@register_schema_type('one_of')
class OneOfType(BaseType):
    def __init__(self, types):
        self.types = types

    def validate(self, value, key):
        valid = set()
        invalid = set()

        reasons = []
        for possible_type in self.types:
            possible_type = get_type_object(possible_type)
            errs = possible_type.validate(value, key)
            if not errs:
                valid.add(possible_type)
            else:
                reasons.append('\n'.join(errs).replace('\n', '\n    '))
                invalid.add(possible_type)
        reasons = '. Tried:\n' + '\n'.join('  - %s' % r for r in reasons)

        if len(valid) > 1:
            return ['Expected %r to be exactly one type,'
                    ' not %d types %r'
                    % (key, len(valid), valid) + reasons]
        elif not valid:
            return ['%r is not one of %r' % (key, invalid) + reasons]
        else:
            return []


@register_schema_type('any_of')
class AnyOfType(BaseType):
    def __init__(self, types):
        self.types = types

    def validate(self, value, key):
        valid = set()
        invalid = set()

        reasons = []
        for possible_type in self.types:
            possible_type = get_type_object(possible_type)
            errs = possible_type.validate(value, key)
            if not errs:
                valid.add(possible_type)
            else:
                reasons.append('\n'.join(errs).replace('\n', '\n    '))
                invalid.add(possible_type)
        reasons = '. Tried:\n' + '\n'.join('  - %s' % r for r in reasons)

        if not valid:
            return ['%r is not one of %r' % (key, invalid) + reasons]
        else:
            return []
