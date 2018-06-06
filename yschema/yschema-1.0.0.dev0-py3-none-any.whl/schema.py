from collections import Mapping
import inspect
from .types import BaseType
from .exceptions import ValidationError, SchemaError


class AliasedType(BaseType):
    def __init__(self, types, constants, typedef, name):
        """
        Make an alias to a defined type. The alias type is created with
        parameter initialization on alias definition time an cannot take
        more parameters when the alias is used
        """
        self.name = name
        self.aliased_type = _make_type(types, constants, typedef, name)

    def validate(self, data, key):
        self.aliased_type.validate(data, key)

    def __repr__(self):
        return '<Alias %s of %r>' % (self.name, self.aliased_type)


class Schema(BaseType):
    def __init__(self, schema_data, types, constants, name='__root__'):
        """
        This is a YSchema parser and validator. The schema is parsed
        when instantiating this class, raising :exception:`SchemaError`
        on errors. This is a subclass of the more general exception
        :exception:`ValidationError`.

        The schema_data describing the schema should be a dictionary.
        After creating this class call :method:`validate`
        """
        self.type_name = name
        self.types = types
        self.constants = constants

        self.keys = {}
        self.required_keys = set()
        self._setup_schema(schema_data)

        # Skip keys starting with underscore. This makes it possible to
        # comment out a subtree with just a single character
        self.skip_private = False

    def _setup_schema(self, schema):
        """
        Parse the schema and any sub schema (defined types) given in the
        schema dictionary
        """
        #  If there is an empty (sub) schema PyYAML will return None
        if schema is None:
            schema = {}

        for key, value in schema.items():
            if key == 'inherit':
                super_type = _make_type(self.types, self.constants,
                                        value, 'super(%s)' % self.type_name)
                if not isinstance(super_type, Schema):
                    raise SchemaError('Invalid super type %r' % super_type)
                self.types.update(super_type.types)
                self.keys.update(super_type.keys)
                self.required_keys.update(super_type.required_keys)
                continue

            cmd, name = key.split()

            if cmd == 'constant':
                self.constants[name] = value
            elif cmd == 'type':
                consts = self.constants.copy()
                types = self.types.copy()
                self.types[name] = Schema(value, types, consts, name=name)
            elif cmd == 'alias':
                self.types[name] = AliasedType(self.types, self.constants,
                                               value, name)
            elif cmd == 'required':
                self.required_keys.add(name)
                self.keys[name] = _make_type(self.types, self.constants,
                                             value, name)
            elif cmd == 'optional':
                self.keys[name] = _make_type(self.types, self.constants,
                                             value, name)
            else:
                raise SchemaError('Unknown schema command %r' % cmd)

    def validate(self, data, key='__root__'):
        """
        Validate the dictionary ``data`` according to this schema. This
        method is recursive and will call itself on sub-dictionaries
        (``self`` will then be a sub-schema). For other value types this
        method will call validate() on one of the types defined in
        :mod:`yschema.types` (or a user defined type). The method raises
        :exception:`ValidationError` if the document is not valid
        according to the schema.
        """
        if self.type_name == '__root__':
            type_name = 'Root document'
        else:
            type_name = self.type_name

        if not isinstance(data, Mapping):
            raise ValidationError('%s: a (sub) dictionary must be a mapping, but'
                                  ' %r got a %s' % (type_name, key, type(data)))

        seen_keys = set()
        for subkey, value in data.items():
            if self.skip_private and subkey.startswith('_'):
                continue
            seen_keys.add(subkey)

            # The key must be registstered, or a '*' key must be present
            if subkey not in self.keys:
                if '*' in self.keys:
                    t = self.keys['*']
                else:
                    raise ValidationError('%s: got unexpected key %r' %
                                          (type_name, subkey))
            else:
                t = self.keys[subkey]

            t.validate(value, subkey)

        diff = self.required_keys.difference(seen_keys)
        if diff:
            raise ValidationError('%s: Missing required keys %r' %
                                  (type_name, diff))


def _get_type(types, type_name, key, params):
    """
    Get a type by name and instantiate it, or raise an appropriate error
    """
    if type_name in types:
        t = types[type_name]
        if inspect.isclass(t):
            return t(**params)

        if params:
            raise SchemaError('Cannot give further parameters to %r in'
                              ' key %r' % (t.type_name, key))
        return t
    else:
        raise ValidationError('The referenced type %r is not defined'
                              % type_name)


def _make_type(types, constants, typedef, key):
    """
    Get an instantiated type class.

    The typedef string can either be just a name 'str', 'int' etc or
    a function call 'int(min_val=2)'. The last one makes the code eval
    "dict(min_val=2)" to get the parameters. In this evaluation the
    given constants dictionary is used.

    The type name must be defined in the types dictionary. The key is
    included only to return better error messages in the exception text.
    """
    i = typedef.find('(')
    if i == -1:
        # Definition without any arguments
        return _get_type(types, typedef.strip(), key, {})

    # The definition includes some arguments
    type_name = typedef[:i].strip()
    code = 'dict%s' % typedef[i:]
    local_vars = constants.copy()
    local_vars.update(types)
    args = eval(code, globals(), local_vars)
    return _get_type(types, type_name, key, args)
