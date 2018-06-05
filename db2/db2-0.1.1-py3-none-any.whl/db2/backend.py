#! usr/bin/python3.6

import re
from datetime import datetime, date, time

'''
This the backend of pydb
Maps FieldTypes to MySQL column names and does all the type checking
for all the model fields

pydb: mysql mapping

Mapper = {
    String: CHAR
    SizedString: VARCHAR(size)
    SizedRegexString: VARCHAR(size) 
    Integer: Integer
    PositiveInteger: Integer
    PositiveFloat: DOUBLE
    DateTimeField: DATETIME
    DateField: DATE
    TimeField: Time
    EnumField: ENUM(values)
    PhoneNumber--> Works a sized String(maxlen)
    ListString: For a string of list "[1,2,3,4,5]" -- list <--__get__(eval(self))
}

NB:
===> The orm assigns an automatic field called id which is used a 
primary key with auto-increment.

Though some fields have similar mysql types, they are type checked 
differently in the application.
'''

__all__ = []

class DescriptorMeta(type):
    '''Metaclass for model fields'''
    def __new__(meta, clsname, bases, clsdict):
        clsobj = super().__new__(meta, clsname, bases, dict(clsdict))

        return clsobj


_contracts = {}

class Descriptor(metaclass=DescriptorMeta):
    '''Implements a Descriptor protocol for type checking of fields
    It's a superclass of all Types
    Keeps a record of all subclasses in a dictionary
    '''

    def __init_subclass__(cls):
        _contracts[cls.__name__] = cls

    def __init__(self, name=None):
        self.name = name

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
    
    def __get__(self, instance, value):
        value = instance.__dict__.get(self.name, None)
        return value


class Typed(Descriptor):
    type = None

    def __set__(self, instance, value):
        if not isinstance(value, self.type):
            raise TypeError('Expected %s, got %s for %s'% (self.type, type(value), self.name))

        super().__set__(instance, value)

    def __repr__(self):
        name = type(self).__name__.lower()
        if name =='liststring':
            return f"Text({self.maxlen})"

        if hasattr(self, 'maxlen') and name != 'liststring':
            return f"VARCHAR({self.maxlen})"

        if name == 'positiveinteger':
            if len(self.kwargs) > 0:
                return "INTEGER PRIMARY KEY AUTO_INCREMENT"
            else:
                return "INTEGER"

        elif name == 'integer':
            return "INTEGER"

        elif name == 'list':
            return 'Text'

        elif name == 'tuple':
            return 'Text'


class Integer(Typed):
    type = int

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        for key in self.kwargs:
            if key not in ['auto_increment', 'primary_key', 'index', 'unique']:
                raise TypeError('Unsupported kwarg %s'%key)

class String(Typed):
    type = str

class Float(Typed):
    type = float

    def __repr__(self):
        return "DOUBLE"

# Value checking
class Positive(Descriptor):
    def __set__(self, instance, value):
        if value < 0:
            raise ValueError('Expected >= 0')
        super().__set__(instance, value)


# More specialized types
class PositiveInteger(Integer, Positive):
    pass


class PositiveFloat(Float, Positive):
    pass


# Length checking
class Sized(Descriptor):
    def __init__(self, *args, maxlen, **kwargs):
        self.maxlen = maxlen
        super().__init__(*args, **kwargs)

    def __set__(self, instance, value):
        if len(value) > self.maxlen:
            raise ValueError('String is too long. Should be <= %s chars'%self.maxlen)
        super().__set__(instance, value)


class SizedString(String, Sized):
    pass


class LongText(String, Sized):
    pass


# Pattern matching
class Regex(Descriptor):
    def __init__(self, *args, pat, **kwargs):
        self.pat = re.compile(pat)
        super().__init__(*args, **kwargs)

    def __set__(self, instance, value):
        if not self.pat.match(value):
            raise ValueError('Invalid string pattern')
        super().__set__(instance, value)


class SizedRegexString(SizedString, Regex):
    pass

class List(Typed):
    type = list

class Tuple(Typed):
    type = tuple


class PhoneNumber(String, Sized):
    pass


class ListString(String, Sized):
    def __set__(self, instance, value):
        if isinstance(value, str):
            import ast
            value = ast.literal_eval(value)
        elif isinstance(value, type(None)):
            value = []
        instance.__dict__[self.name] = value

    def __get__(self, instance, value):
        value = instance.__dict__.get(self.name, None)
        if isinstance(value, str):
            import ast
            value = ast.literal_eval(value)
        elif isinstance(value, type(None)):
            value = []

        return value

class DateField(Typed):
    type = date

    def __init__(self, fmt='%Y-%m-%d'):
        self.fmt = fmt

    def __set__(self, instance, value):
        try:
            self.dt = datetime.strptime(value, self.fmt).date()
        except Exception as e:
            raise e
        super().__set__(instance, self.dt)

    def __repr__(self):
        return "DATE"

class TimeField(Typed):
    type = time

    def __init__(self, fmt='%H:%M:%S'):
        self.fmt = fmt

    def __set__(self, instance, value):
        try:
            self.time = datetime.now().time()                
        except Exception as e:
            raise e

        super().__set__(instance, self.time)

    def __repr__(self):
        return 'TIME'


class DateTimeField(Typed):
    type = datetime

    def __init__(self, fmt='%Y-%m-%d %H:%M:%S', auto_now_add=True):
        self.fmt = fmt
        self.auto_now_add = auto_now_add

    def __set__(self, instance, value):
        try:
            self.dt = datetime.strptime(value, self.fmt)
        except Exception as e:
            raise e

        super().__set__(instance, self.dt)

    def __repr__(self):
        if self.auto_now_add:
            return "DATETIME DEFAULT CURRENT_TIMESTAMP"
        else:
            return "DATETIME"

class EnumField(Descriptor):
    type = 'enum'

    def __init__(self, values):
        self.values = values

    def __set__(self, instance, value):
        if value not in self.values:
            raise TypeError('%s is not valid.Expected one of %s'%(value, self.values))
        super().__set__(instance, value)

    def __repr__(self):
        return f"ENUM{self.values}"

