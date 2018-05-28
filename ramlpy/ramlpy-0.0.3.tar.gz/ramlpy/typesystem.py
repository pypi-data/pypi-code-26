import re
import typing
from collections import OrderedDict, namedtuple
from enum import Enum

from .utils import snake_case, topological_sort


ConfiguredTypeClass = namedtuple('ConfiguredTypeClass', ['cls', 'kwargs'])


class ValidationError(ValueError):
    __slots__ = ('message', 'field', 'errors')

    def __init__(
        self, message: str, *, field: str = None,
        errors: typing.Union[
            typing.List["ValidationError"],
            typing.Mapping[str, "ValidationError"]
        ] = None
    ):
        self.message = message
        self.field = field
        self.errors = errors


class RAMLTypeError(RuntimeError):
    pass


class Any:
    DEFINITION = 'any'
    BASES = {'any'}
    __slots__ = (
        'registry', 'name', 'display_name', 'description',
        'required', 'default', 'example', 'examples', 'enum'
    )

    def __init__(
        self, *,
        registry: "Registry",
        display_name: str = None,
        description: str = None,
        required: bool = True,
        enum: typing.Iterable = None,
        default=None,
        example=None,
        examples: typing.Mapping[str, typing.Any] = None
    ):
        self.registry = registry
        self.display_name = display_name
        self.description = description
        self.required = required
        self.enum = enum
        self.default = default
        self.example = example
        self.examples = examples

    def set_defaults(self, value):
        if value is None and self.default is not None:
            value = self.default
        return value

    def validate(self, value):
        if self.required and value is None:
            raise ValidationError('Missing value for the required field')

        if self.enum and value not in self.enum:
            raise ValidationError(
                'Value %s does not match allowed values' % value
            )

    @staticmethod
    def get_derived_class() -> typing.ClassVar:
        return DerivedAny


class Boolean(Any):
    DEFINITION = 'boolean'
    BASES = {'any', 'boolean'}

    def validate(self, value):
        super().validate(value)

        if value is not None and type(value) is not bool:
            raise ValidationError('Value is expected to be boolean')

    @staticmethod
    def get_derived_class() -> typing.ClassVar:
        return DerivedBoolean


class String(Any):
    DEFINITION = 'string'
    BASES = {'any', 'string'}
    __slots__ = ('pattern', 'min_length', 'max_length')

    def __init__(
        self, *, pattern: str = None, min_length: int = 0,
        max_length: int = 2147483647, **kwargs
    ):
        super().__init__(**kwargs)
        self.pattern = pattern
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value):
        super().validate(value)

        if value is None:
            return

        if type(value) is not str:
            raise ValidationError('Value is expected to be string')

        value_length = len(value)
        if self.max_length and value_length > self.max_length:
            raise ValidationError(
                'Value is too long: given %d, max allowed %d' % (
                    value_length, self.max_length
                )
            )

        if self.min_length and value_length < self.min_length:
            raise ValidationError(
                'Value is too short: given %d, min allowed %d' % (
                    value_length, self.max_length
                )
            )

        if self.pattern:
            if re.match(self.pattern, value) is None:
                raise ValidationError(
                    'Value %s does not match pattern %s' % (
                        value, self.pattern
                    )
                )

    @staticmethod
    def get_derived_class() -> typing.ClassVar:
        return DerivedString


class NumberFormat(Enum):
    """
    int8: (-128 to 127)
    int16: (-32,768 to +32,767)
    int32, int: (-2,147,483,648 to +2,147,483,647)
    int64, long: (-9,223,372,036,854,775,808 to +9,223,372,036,854,775,807)
    """
    int = 'int'
    int8 = 'int8'
    int16 = 'int16'
    int32 = 'int32'
    int64 = 'int64'
    long = 'long'


class Number(Any):
    DEFINITION = 'number'
    BASES = {'any', 'number'}

    __slots__ = ('minimum', 'maximum', 'format', 'multiple_of')

    def __init__(
        self, *,
        minimum: typing.Union[int, float] = None,
        maximum: typing.Union[int, float] = None,
        format: NumberFormat = None,
        multiple_of: typing.Union[int, float] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.minimum = minimum
        self.maximum = maximum
        self.format = format
        self.multiple_of = multiple_of

    def validate(self, value):
        super().validate(value)

        if value is None:
            return

        if type(value) not in (float, int):
            raise ValidationError('Value is expected to be number')

        if self.minimum is not None and self.minimum > value:
            raise ValidationError(
                'Value %r is less than allowed minimum %r' % (
                    value, self.minimum
                )
            )

        if self.maximum is not None and self.maximum < value:
            raise ValidationError(
                'Value %r is geater than allowed maximum %r' % (
                    value, self.maximum
                )
            )

        if self.multiple_of is not None and value % self.multiple_of != 0:
            raise ValidationError(
                'Value %r is not divisible with %r' % (value, self.multiple_of)
            )

        if self.format is not None:
            # FIXME: currently not clear in documentation how to validate
            raise NotImplementedError()

    @staticmethod
    def get_derived_class() -> typing.ClassVar:
        return DerivedNumber


class Integer(Number):
    DEFINITION = 'integer'
    BASES = {'any', 'number', 'integer'}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def validate(self, value):
        Any.validate(self, value)
        if value is not None and type(value) is not int:
            raise ValidationError('Value is expected to be integer')

    @staticmethod
    def get_derived_class() -> typing.ClassVar:
        return DerivedInteger


class DateOnly(Any):
    DEFINITION = 'date-only'
    BASES = {'any', 'date-only'}

    def validate(self, value: str):
        super().validate(value)
        raise NotImplementedError()

    @staticmethod
    def get_derived_class() -> typing.ClassVar:
        return DerivedDateOnly


class TimeOnly(Any):
    DEFINITION = 'time-only'
    BASES = {'any', 'time-only'}

    def validate(self, value: str):
        super().validate(value)
        raise NotImplementedError()

    @staticmethod
    def get_derived_class() -> typing.ClassVar:
        return DerivedTimeOnly


class DateTimeOnly(Any):
    DEFINITION = 'datetime-only'
    BASES = {'any', 'datetime-only'}

    def validate(self, value: str):
        super().validate(value)
        raise NotImplementedError()

    @staticmethod
    def get_derived_class() -> typing.ClassVar:
        return DerivedDateTimeOnly


class DateFormat(Enum):
    rfc3339 = 'rfc3339'
    rfc2616 = 'rfc2616'


class DateTime(Any):
    DEFINITION = 'datetime'
    BASES = {'any', 'datetime'}
    __slots__ = ('format', )

    def __init__(self, *, format: DateFormat = None, **kwargs):
        super().__init__(**kwargs)
        self.format = format

    def validate(self, value: str):
        super().validate(value)
        raise NotImplementedError()

    @staticmethod
    def get_derived_class() -> typing.ClassVar:
        return DerivedDateTime


class File(Any):
    DEFINITION = 'file'
    BASES = {'any', 'file'}
    __slots__ = ('file_types', 'min_length', 'max_length')

    def __init__(
        self, *,
        file_types: typing.List[str] = None,
        min_length: int = 0,
        max_length: int = 2147483647,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.file_types = file_types
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value):
        super().validate(value)
        raise NotImplementedError()

    @staticmethod
    def get_derived_class() -> typing.ClassVar:
        return DerivedFile


class Nil(Any):
    DEFINITION = 'nil'
    BASES = {'any', 'nil'}

    def validate(self, value: None):
        if value is not None:
            raise ValidationError('Value is expected to be nil / null / None')

    @staticmethod
    def get_derived_class() -> typing.ClassVar:
        return DerivedNil


class Array(Any):
    DEFINITION = 'array'
    BASES = {'any', 'array'}
    __slots__ = ('unique_items', 'items', 'min_items', 'max_items')

    def __init__(
        self, *,
        unique_items: bool = False,
        items: Any = None,
        min_items: int = 0,
        max_items: int = 2147483647,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.unique_items = unique_items
        self.items = items
        self.min_items = min_items
        self.max_items = max_items

    def validate(self, value):
        super().validate(value)

        if value is None:
            return

        if type(value) is not list:
            raise ValidationError('Value is expected to be list')

        if self.items is not None:
            for value_item in value:
                self.items.validate(value_item)

        value_length = len(value)
        if (self.max_items is not None) and (value_length > self.max_items):
            raise ValidationError('Too many items: given %d, allowed %d' % (
                value_length, self.max_items
            ))

        if (self.min_items is not None) and (value_length < self.min_items):
            raise ValidationError(
                'Not enough items: given %d, minimum required %d' % (
                    value_length, self.min_items
                )
            )

        if self.unique_items:
            raise NotImplementedError()

    @staticmethod
    def get_derived_class() -> typing.ClassVar:
        return DerivedArray


class Object(Any):
    DEFINITION = 'object'
    BASES = {'any', 'object'}
    __slots__ = (
        'properties', 'min_properties', 'max_properties',
        'additional_properties', 'discriminator', 'discriminator_value'
    )

    def __init__(
        self, *,
        properties: typing.Mapping[str, Any] = None,
        min_properties: int = None,
        max_properties: int = None,
        additional_properties: bool = True,
        discriminator: str = None,
        discriminator_value: str = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.properties = properties or dict()
        self.min_properties = min_properties
        self.max_properties = max_properties
        self.additional_properties = additional_properties
        self.discriminator = discriminator
        self.discriminator_value = discriminator_value

    def validate(self, value):
        super().validate(value)

        if value is None:
            return

        if type(value) is not dict:
            raise ValidationError('Value is expected to be object')

        errors = {}
        for property_name, property in self.properties.items():
            try:
                property.validate(value.get(property_name))
            except ValidationError as error:
                errors[property_name] = error

        if errors:
            raise ValidationError('Object contains errors', errors=errors)

        defined_properties_number = len(self.properties)
        if (
            self.min_properties is not None and
            self.min_properties > defined_properties_number
        ):
            raise ValidationError(
                'Object should have at least %d properties, %d provided' % (
                    self.min_properties, defined_properties_number
                )
            )

        if (
            self.max_properties is not None and
            self.max_properties < defined_properties_number
        ):
            raise ValidationError(
                'Object should have maximum %d properties, %d provided' % (
                    self.max_properties, defined_properties_number
                )
            )

    @staticmethod
    def get_derived_class() -> typing.ClassVar:
        return DerivedObject


class DerivedAny(Any):
    __slots__ = ('ancestors', )

    def __init__(self, *, ancestors: typing.List[Any], **kwargs):
        super().__init__(**kwargs)

        for ancestor in ancestors:
            if not self.BASES.issuperset(ancestor.BASES):
                raise ValueError(
                    'Ancestor types incompatible: [%s, %s]' % (
                        self.BASES, ancestor.BASES
                    )
                )

        self.ancestors = ancestors

    def validate(self, value):
        for ancestor in self.ancestors:
            ancestor.validate(value)

        super().validate(value)


class DerivedBoolean(Boolean):
    __slots__ = ('ancestors', )

    def __init__(self, *, ancestors: typing.List[Boolean], **kwargs):
        super().__init__(**kwargs)

        for ancestor in ancestors:
            if not self.BASES.issuperset(ancestor.BASES):
                raise ValueError(
                    'Ancestor types incompatible: [%s, %s]' % (
                        self.BASES, ancestor.BASES
                    )
                )

        self.ancestors = ancestors

    def validate(self, value):
        for ancestor in self.ancestors:
            ancestor.validate(value)
        super().validate(value)


class DerivedString(String):
    __slots__ = ('ancestors',)

    def __init__(self, *, ancestors: typing.List[String], **kwargs):
        super().__init__(**kwargs)

        for ancestor in ancestors:
            if not self.BASES.issuperset(ancestor.BASES):
                raise ValueError(
                    'Ancestor types incompatible: [%s, %s]' % (
                        self.BASES, ancestor.BASES
                    )
                )

        self.ancestors = ancestors

    def validate(self, value):
        for ancestor in self.ancestors:
            ancestor.validate(value)
        super().validate(value)


class DerivedNumber(Number):
    __slots__ = ('ancestors',)

    def __init__(self, *, ancestors: typing.List[Number], **kwargs):
        super().__init__(**kwargs)

        for ancestor in ancestors:
            if not self.BASES.issuperset(ancestor.BASES):
                raise ValueError(
                    'Ancestor types incompatible: [%s, %s]' % (
                        self.BASES, ancestor.BASES
                    )
                )

        self.ancestors = ancestors

    def validate(self, value):
        for ancestor in self.ancestors:
            ancestor.validate(value)
        super().validate(value)


class DerivedInteger(Integer):
    __slots__ = ('ancestors',)

    def __init__(self, *, ancestors: typing.List[Integer], **kwargs):
        super().__init__(**kwargs)

        for ancestor in ancestors:
            if not self.BASES.issuperset(ancestor.BASES):
                raise ValueError(
                    'Ancestor types incompatible: [%s, %s]' % (
                        self.BASES, ancestor.BASES
                    )
                )

        self.ancestors = ancestors

    def validate(self, value):
        for ancestor in self.ancestors:
            ancestor.validate(value)
        super().validate(value)


class DerivedDateOnly(DateOnly):
    __slots__ = ('ancestors', )

    def __init__(self, *, ancestors: typing.List[DateOnly], **kwargs):
        super().__init__(**kwargs)

        for ancestor in ancestors:
            if not self.BASES.issuperset(ancestor.BASES):
                raise ValueError(
                    'Ancestor types incompatible: [%s, %s]' % (
                        self.BASES, ancestor.BASES
                    )
                )

        self.ancestors = ancestors

    def validate(self, value):
        for ancestor in self.ancestors:
            ancestor.validate(value)
        super().validate(value)


class DerivedTimeOnly(TimeOnly):
    __slots__ = ('ancestors',)

    def __init__(self, *, ancestors: typing.List[TimeOnly], **kwargs):
        super().__init__(**kwargs)

        for ancestor in ancestors:
            if not self.BASES.issuperset(ancestor.BASES):
                raise ValueError(
                    'Ancestor types incompatible: [%s, %s]' % (
                        self.BASES, ancestor.BASES
                    )
                )

        self.ancestors = ancestors

    def validate(self, value):
        for ancestor in self.ancestors:
            ancestor.validate(value)
        super().validate(value)


class DerivedDateTimeOnly(DateTimeOnly):
    __slots__ = ('ancestors',)

    def __init__(self, *, ancestors: typing.List[DateTimeOnly], **kwargs):
        super().__init__(**kwargs)

        for ancestor in ancestors:
            if not self.BASES.issuperset(ancestor.BASES):
                raise ValueError(
                    'Ancestor types incompatible: [%s, %s]' % (
                        self.BASES, ancestor.BASES
                    )
                )

        self.ancestors = ancestors

    def validate(self, value):
        for ancestor in self.ancestors:
            ancestor.validate(value)
        super().validate(value)


class DerivedDateTime(DateTime):
    __slots__ = ('ancestors',)

    def __init__(self, *, ancestors: typing.List[DateTime], **kwargs):
        super().__init__(**kwargs)

        for ancestor in ancestors:
            if not self.BASES.issuperset(ancestor.BASES):
                raise ValueError(
                    'Ancestor types incompatible: [%s, %s]' % (
                        self.BASES, ancestor.BASES
                    )
                )

        self.ancestors = ancestors

    def validate(self, value):
        for ancestor in self.ancestors:
            ancestor.validate(value)
        super().validate(value)


class DerivedFile(File):
    __slots__ = ('ancestors',)

    def __init__(self, *, ancestors: typing.List[File], **kwargs):
        super().__init__(**kwargs)

        for ancestor in ancestors:
            if not self.BASES.issuperset(ancestor.BASES):
                raise ValueError(
                    'Ancestor types incompatible: [%s, %s]' % (
                        self.BASES, ancestor.BASES
                    )
                )

        self.ancestors = ancestors

    def validate(self, value):
        for ancestor in self.ancestors:
            ancestor.validate(value)
        super().validate(value)


class DerivedNil(Nil):
    __slots__ = ('ancestors',)

    def __init__(self, *, ancestors: typing.List[Nil], **kwargs):
        super().__init__(**kwargs)

        for ancestor in ancestors:
            if not self.BASES.issuperset(ancestor.BASES):
                raise ValueError(
                    'Ancestor types incompatible: [%s, %s]' % (
                        self.BASES, ancestor.BASES
                    )
                )

        self.ancestors = ancestors

    def validate(self, value):
        for ancestor in self.ancestors:
            ancestor.validate(value)
        super().validate(value)


class DerivedArray(Array):
    __slots__ = ('ancestors',)

    def __init__(self, *, ancestors: typing.List[Array], **kwargs):
        super().__init__(**kwargs)

        for ancestor in ancestors:
            if not self.BASES.issuperset(ancestor.BASES):
                raise ValueError(
                    'Ancestor types incompatible: [%s, %s]' % (
                        self.BASES, ancestor.BASES
                    )
                )

        self.ancestors = ancestors

    def validate(self, value):
        for ancestor in self.ancestors:
            ancestor.validate(value)
        super().validate(value)


class DerivedObject(Object):
    __slots__ = ('ancestors',)

    def __init__(self, *, ancestors: typing.List[Object], **kwargs):
        super().__init__(**kwargs)

        for ancestor in ancestors:
            if not self.BASES.issuperset(ancestor.BASES):
                raise ValueError(
                    'Ancestor types incompatible: [%s, %s]' % (
                        self.BASES, ancestor.BASES
                    )
                )

        self.ancestors = ancestors

    def validate(self, value):
        for ancestor in self.ancestors:
            ancestor.validate(value)
        super().validate(value)


class Union(Any):
    DEFINITION = None
    __slots__ = ('members', )

    def __init__(self, *, members: typing.Set[Any], **kwargs):
        super().__init__(**kwargs)
        self.members = members

    def validate(self, value):
        super().validate(value)

        errors = []
        for member in self.members:
            try:
                member.validate(value)
                break
            except ValidationError as error:
                errors.append(error)

        else:
            raise ValidationError(
                'All union members failed', errors=errors
            )

    @staticmethod
    def get_derived_class() -> typing.ClassVar:
        raise NotImplementedError()

    @staticmethod
    def detect_derived_class(members) -> typing.ClassVar:
        result = None

        for member in members:
            if result is None or member.BASES.issuperset(result.BASES):
                result = member.__class__

            elif not member.BASES.issubset(result.BASES):
                raise RAMLTypeError(
                    'Unable to detect derived class: '
                    '%s %s types are not compatible' % (
                        member.__class__, result
                    )
                )


BUILTIN_TYPES = [
    Any, Array, Boolean, DateOnly, DateTime, DateTimeOnly,
    File, Integer, Nil, Number, Object, String, TimeOnly
]


class Registry:
    BUILTIN_TYPE_CLASS_MAP = {
        builtin_type.DEFINITION: builtin_type
        for builtin_type in BUILTIN_TYPES
    }

    def __init__(self, types: typing.Dict[str, typing.Any] = None):
        self.named_types = OrderedDict()

        if types:
            self.bulk_register(types)

    def register(
        self, name: str,
        definition: typing.Union[str, typing.Dict[str, typing.Any]]
    ) -> Any:
        """ Add declaration with given name to registry instance. """
        self.named_types[name] = self.factory(definition=definition)
        return self.named_types[name]

    def bulk_register(self, named_definitions: typing.Dict[str, typing.Any]):
        """ Add multiple named declarations to registry instance. """
        dependencies = [
            [name, self.parse_dependencies(definition)]
            for name, definition in named_definitions.items()
        ]
        sorted_definitions = topological_sort(dependencies)

        for name in sorted_definitions:
            self.register(name=name, definition=named_definitions[name])

    @classmethod
    def normalize_definition(
        cls, definition: typing.Union[str, typing.Dict[str, typing.Any]]
    ) -> typing.Dict[str, typing.Any]:
        if type(definition) is str:
            definition = {'type': definition}

        if type(definition) is not dict:
            raise RAMLTypeError(
                'Type definition has invalid type, str or dict expected'
            )

        if definition.get('type') is None:
            if 'properties' in definition:
                definition['type'] = Object.DEFINITION
            else:
                definition['type'] = Any.DEFINITION

        return definition

    @classmethod
    def parse_dependencies(
        cls, definition: typing.Union[str, typing.Dict[str, typing.Any]]
    ) -> typing.Set[str]:
        """ Get named types dependency set for given definition. """
        definition = cls.normalize_definition(definition)

        # Arrays can have depencencies in items attribute
        if definition['type'] == Array.DEFINITION and 'items' in definition:
            return cls.parse_dependencies(definition.get('items'))

        # Objects can contain dependencies in properties attribute
        elif definition['type'] == Object.DEFINITION and 'properties' in definition:
            dependencies = []
            for _, property in definition.get('properties').items():
                dependencies.extend(cls.parse_dependencies(property))
            return set(dependencies)

        # Simple cases, just definition type
        else:
            def_type = definition['type']
            for special_char in ['(', ')', '[', ']', ',', '|']:
                def_type = def_type.replace(special_char, ' ')

        dependencies = set(def_type.split()) - set(cls.BUILTIN_TYPE_CLASS_MAP.keys())
        if dependencies:
            pass
        return dependencies

    def configure_type_class(self, declaration: str) -> ConfiguredTypeClass:
        if declaration in self.BUILTIN_TYPE_CLASS_MAP.keys():
            return self.BUILTIN_TYPE_CLASS_MAP[declaration], {'registry': self}

        elif declaration in self.named_types:
            parent_type_instance = self.named_types[declaration]
            return (
                parent_type_instance.get_derived_class(), {
                    'registry': self,
                    'ancestors': [parent_type_instance]
                }
            )
        else:
            raise RAMLTypeError('Unknown type %s', declaration)

    @staticmethod
    def definition_is_simple(definition: str) -> bool:
        for special_char in [',', '|', '(', ')', '[', ']']:
            if special_char in definition:
                return False
        return True

    def handle_chunks(
        self,
        chunks: typing.List[typing.Tuple],
        delimiter: str
    ) -> typing.Tuple:

        # Union chunks
        if delimiter == '|':
            members = []
            for class_instance, class_kwargs in chunks:
                members.append(class_instance(**class_kwargs))

            return Union, {'registry': self, 'members': members}

        # Derived
        elif delimiter == ',':
            ancestors = []
            derived_class = None

            for class_instance, class_kwargs in chunks:
                if class_instance is Union:
                    union_derived_type = Union.detect_derived_class(
                        class_kwargs['members']
                    )

                    if derived_class is None:
                        derived_class = union_derived_type
                    elif union_derived_type.BASES.issuperset(derived_class.BASES):
                        derived_class = union_derived_type
                    elif not class_instance.BASES.issubset(derived_class.BASES):
                        raise ValueError('Incompatible types: %s %s' % (
                            class_instance.DEFINITION, derived_class.DEFINITION
                        ))

                    ancestors.append(class_instance(**class_kwargs))

                else:
                    if derived_class is None:
                        derived_class = class_instance

                    elif class_instance.BASES.issuperset(derived_class.BASES):
                        derived_class = class_instance

                    elif not class_instance.BASES.issubset(derived_class.BASES):
                        raise ValueError('Incompatible types: %s %s' % (
                            class_instance.DEFINITION, derived_class.DEFINITION
                        ))

                    ancestors.append(class_instance(**class_kwargs))

            return derived_class.get_derived_class(), {
                'registry': self, 'ancestors': ancestors
            }

        else:
            raise ValueError('Unsupported delimiter %s' % delimiter)

    def parse_definition(self, definition: str) -> tuple:
        definition = definition.strip()

        if self.definition_is_simple(definition):
            return self.configure_type_class(definition)

        chunks = []
        buffer = []  # chunk to be processed

        nested = 0
        last_delimiter = None  # required to group chunks in Union / Derived
        current_chunk = None  # chunk that can be used to apply [] modifiers
        previous_char = None

        for char in definition:
            if char == '(':
                nested += 1

            elif char == ')':
                nested -= 1
                if nested == 0:
                    # Parse group into modifiable chunk
                    assert current_chunk is None
                    current_chunk = self.parse_definition(''.join(buffer))
                    buffer = []

            elif char == '[':
                pass

            elif char == ']' and previous_char == '[' and nested == 0:
                if ''.join(buffer).strip():
                    assert current_chunk is None  # not flushed
                    current_chunk = self.parse_definition(''.join(buffer))
                    buffer = []

                if current_chunk:
                    items_class, items_class_kwargs = current_chunk
                    current_chunk = Array, {
                        'registry': self,
                        'items': items_class(**items_class_kwargs)
                    }
                else:
                    current_chunk = Array, {'registry': self}

            elif char in ',|' and not nested:
                if ''.join(buffer).strip():
                    assert current_chunk is None
                    current_chunk = self.parse_definition(''.join(buffer))
                    buffer = []

                chunks.append(current_chunk)
                current_chunk = None

                if last_delimiter != char and len(chunks) > 1:
                    chunks = [self.handle_chunks(chunks, last_delimiter)]

                last_delimiter = char
            else:
                buffer.append(char)

            previous_char = char

        if ''.join(buffer).strip():
            assert current_chunk is None
            current_chunk = self.parse_definition(''.join(buffer))
            buffer = []

        if current_chunk:
            chunks.append(current_chunk)
            current_chunk = None

        if len(chunks) > 1:
            return self.handle_chunks(chunks, last_delimiter)

        return chunks[0]

    def factory(
        self, definition: typing.Union[str, typing.Mapping[str, Any]],
    ) -> Any:
        """ Instantiate data type from given declaration. """
        definition = self.normalize_definition(definition)

        kwargs = {'registry': self}
        for key, value in definition.items():
            if key not in ['type', 'properties']:
                kwargs[snake_case(key)] = value

        cls, specific_kwargs = self.parse_definition(
            definition.get('type')
        )

        if cls in (Object, DerivedObject) and 'properties' in definition:
            # FIXME: tests for this shit!
            kwargs['properties'] = {}
            for property, property_value in definition['properties'].items():
                kwargs['properties'][property] = self.factory(property_value)

        if cls in (Array, DerivedArray) and 'items' in definition:
            # FIXME: tests for this shit!
            kwargs['items'] = self.factory(definition.get('items'))

        return cls(**{**kwargs, **specific_kwargs})
