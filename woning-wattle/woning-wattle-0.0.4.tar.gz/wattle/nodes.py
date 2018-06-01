class NotSet(object):
    pass


class NoValue(object):
    pass


class Node(object):
    def __init__(self, type, *, required=True, default=NotSet):
        assert not (required is False and default is NotSet), \
            'default must be set when requires is False'
        self.type = type
        # set required to False is default is provided
        if default is not NotSet and required:
            required = False
        self.required = required
        self.default = default

    def get_fields(self):
        """List the fields defined on the wrapped type.
        
        Returns an empty list for wrapped builtins.
        """
        fields = []
        for attr_name in dir(self.type):
            attr_val = getattr(self.type, attr_name)
            if isinstance(attr_val, (Value, Nested)):
                fields.append((attr_name, attr_val))
        return fields

    def load(self, data):
        """Loads the object or value from data. 
        
        This handles the value constraints and passes the actual loading to
        self.load_from_data
        """
        if data is NoValue and self.required:
            if self.default is NotSet:
                raise ValueError('Missing value in {}'.format(self))
            else:
                data = self.default
        return self.load_from_data(data)

    def load_from_data(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<{} of type {}>".format(self.__class__.__name__, self.type)


class Value(Node):
    def load_from_data(self, data):
        return self.type(data)


class Nested(Node):
    def load_from_data(self, data):
        instance = self.type()
        for field_name, field_type in self.get_fields():
            data_obj = data.get(field_name, NoValue)
            try:
                loaded_value = field_type.load(data_obj)
            except ValueError as e:
                raise ValueError('Missing {} from {}'.format(
                    field_name, self.type.__name__))
            setattr(instance, field_name, loaded_value)
        return instance


def create_base_value(name, from_type):
    def __init__(self, required=True, default=NotSet):
        super().__init__(from_type, required=required,
                         default=default)

    return type(name, (Value,), {'__init__': __init__})


Integer = create_base_value('Integer', int)
Float = create_base_value('Float', float)
String = create_base_value('String', str)
Boolean = create_base_value('Boolean', bool)
