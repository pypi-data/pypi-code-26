class ValidationError(Exception):
    pass


class SchemaTypeError(ValidationError):
    pass


class SchemaError(ValidationError):
    pass
