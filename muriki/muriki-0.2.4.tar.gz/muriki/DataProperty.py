#!/usr/bin/env python
# =====================================================================
# Copyright 2018 Humberto Ramos Costa. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or 
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =====================================================================
import re
from gettext import gettext as _
from aenum import Enum, skip
from datetime import *

import decimal 

# TO be used as a constant


class auto_increment(object):
    pass


class Sql(Enum):
    @skip
    class ColumnType(Enum):
        AUTO_INCREMENT = 0
        PRIMARY_KEY = 1
        INDEX = 2
        SIMPLE = 3
#        NO = 4

    @skip
    class Mysql(Enum):
        bool = '{0} BOOLEAN'
        int = '{0} INTEGER'
        biginteger = '{0} BIGINT'
        Decimal = '{0} DECIMAL'
        float = '{0} FLOAT'
        long = '{0} DOUBLE'
        date = '{0} DATE'
        datetime = '{0} DATETIME'
        time = '{0} TIME'
        str = '{0} VARCHAR'
        text = '{0} TEXT'
        bigtext = '{0} LONGTEXT'
        auto_increment = '{0} AUTO_INCREMENT'
        primary_key = 'PRIMARY KEY ({0})'
        index = 'ALTER TABLE {0} ADD INDEX ({1});'
        create_table = 'CREATE TABLE IF NOT EXISTS'
        insert = """INSERT INTO {0}({1})VALUES({2});"""
        value_place_holder= '%s'

    @skip
    class Postgresql(Enum):
        bool = '{0} BOOLEAN'
        int = '{0} INTEGER'
        biginteger = '{0} BIGINT'
        Decimal = '{0} DECIMAL'
        float = '{0} FLOAT'
        long = '{0} DOUBLE'
        date = '{0} DATE'
        datetime = '{0} DATETIME'
        time = '{0} TIME'
        str = '{0} VARCHAR'
        text = '{0} TEXT'
        bigtext = '{0} LONGTEXT'
        auto_increment = '{0} SERIAL'
        primary_key = 'PRIMARY KEY ({0})'
        index = 'CREATE INDEX  IF NOT EXISTS {0}_idx_{1} ON {0}({1});'
        create_table = 'CREATE TABLE IF NOT EXISTS'
        insert = """INSERT INTO {0}({1})VALUES({2});"""
        value_place_holder= '%s'
        
    @skip
    class Sqlite(Enum):
        bool = '{0} BOOLEAN'
        int = '{0} INTEGER'
        biginteger = '{0} BIGINT'
        Decimal = '{0} DECIMAL'
        float = '{0} FLOAT'
        long = '{0} DOUBLE'
        date = '{0} DATE'
        datetime = '{0} DATETIME'
        time = '{0} TIME'
        str = '{0} TEXT'
        text = '{0} TEXT'
        bigtext = '{0} LONGTEXT'
        auto_increment = '{0} SERIAL'
        primary_key = 'PRIMARY KEY ({0})'
        index = 'CREATE INDEX  IF NOT EXISTS {0}_idx ON {0}({1});'
        create_table = 'CREATE TABLE IF NOT EXISTS'
        insert = """INSERT INTO {0}({1})VALUES({2});"""
        value_place_holder= '?'


DEFAULT_STR_LEN = 30
DEFAULT_DECIMAL_TOTAL_DIGITS = 10
DEFAULT_DECIMAL_FRACTION_DIGITS = 2
BIG_TEXT_MIN_LEN = 16000
INT_MIN_VALUE = -2147483648
INT_MAX_VALUE = 2147483647


WhiteSpaceBehaviour = Enum('WhiteSpaceBehaviour', 'PRESERVE REPLACE COLLAPSE')


class DataProperty(object):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            #~ print( k, v )
            if (v is not None):
                setattr(self, k, v)

        if not(hasattr(self, 'data_type')):
            self.data_type = str

        try:
            self._name = self.fget.__name__
        except AttributeError:
            try:
                self._name = self.fset.__name__
            except AttributeError:
                try:
                    self._name = self.place_holder_function.__name__
                    self.fget = self.auto_get
                    self.fset = self.auto_set
                    self.fdel = self.auto_del
                except AttributeError:
                    ValueError(
                        _("Neither fget, fset or "
                            "place_holder_function are defined")
                    )

    def auto_get(self, obj):
        tmp = getattr(obj, '_' + self._name, None)
        if(tmp is None):
            tmp = getattr(self, 'default_value', None)
        return tmp

    def auto_set(self, obj, value):
        setattr(obj, '_' + self._name, value)

    def auto_del(self, obj):
        return delattr(obj, '_' + self._name)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return self.fget(obj)
        except AttributeError:
            raise AttributeError(
                generate_error_message(
                    _("No defined getter for {0}, "
                        "can't read the value"), self._name)
            )

    def __set__(self, obj, value):

        value = self.validate(value)
        try:
            self.fset(obj, value)
        except AttributeError:
            raise AttributeError(
                generate_error_message(
                    _("No defined setter for {0}, "
                        "can't write the value"), self._name)
            )

    def __delete__(self, obj):
        try:
            self.fdel(obj)
        except AttributeError:
            raise AttributeError(
                generate_error_message(
                    _("No defined deleter for {0}, "
                        " can't delete attribute"), self._name)
            )

    def getter(self, fget):
        tmp = vars(self)
        tmp['fget'] = fget
        return type(self)(**tmp)

    def setter(self, fset):
        tmp = vars(self)
        tmp['fset'] = fset
        return type(self)(**tmp)

    def deleter(self, fdel):
        tmp = vars(self)
        tmp['fdel'] = fdel
        return type(self)(**tmp)

    def check_allow_none(self, value):
        if(not(self.allow_none) and value is None):
            raise ValueError(
                generate_error_message(
                    _("Value for {0} can't be None"), self._name
                )
            )

    def validate(self, value):

        # ~ value=check_allow_none( value )
        try:
            self.check_allow_none(value)
        except AttributeError:
            pass  # Validator isn't created

        try:
            value = self.process_white_spaces(value)
        except AttributeError:
            pass  # Validator isn't created

        if(hasattr(self, 'data_type')):
            value = self.convert(value)

        checks = [
            self.check_length, self.check_min_length,
            self.check_max_length, self.check_valid_values,
            self.check_pattern, self.check_max_exclusive,
            self.check_max_inclusive, self.check_min_exclusive,
            self.check_min_inclusive

        ]
        for check in checks:
            try:
                if (value is not None):
                    check(value)
            except AttributeError:
                pass

        return value

    def check_length(self, value):
        if ((len(str(value)) != self.length)):
            raise ValueError(
                generate_error_message(
                    _("Value: {0}, invalid length:{1}, should be: {2}"),
                        str(value), len( str(value)), self.length))

    def check_min_length(self, value):
        if ((len(str(value)) < self.min_length)):
            raise ValueError(
                generate_error_message(
                    _("Value: {0}, invalid length:{1}, mininum: {2}"), value
                        , len( str(value)), self.min_length))

    def check_max_length(self, value):
        if(len(str(value)) > self.max_length):
            raise ValueError(
                generate_error_message(
                    _("Value: {0}, invalid length:{1}, maximum: {2}"), value
                        , len( str(value)), self.max_length))

    def check_valid_values(self, value):
        if (not(value in self.valid_values)):
            raise ValueError(
                generate_error_message(
                    _("Value: {0}, is not in valid values: {1}"),
                    value,
                    self.valid_values))

    def check_pattern(self, value):
        if (not(re.match(r'' + self.pattern, str(value)))):
            raise ValueError(
                generate_error_message(
                    _("Value: {0}, didn't match check pattern: {1}"),
                    value,
                    self.pattern))

    def check_max_exclusive(self, value):
        if (value >= self.max_exclusive):
            raise ValueError(
                generate_error_message(
                    _("Value {0} is greater or equal upper limit : {1}"),
                    value,
                    self.max_exclusive))

    def check_max_inclusive(self, value):
        if (value > self.max_inclusive):
            raise ValueError(
                generate_error_message(
                    _("Value {0} is greater than limit : {1}"),
                    value,
                    self.max_inclusive))

    def check_min_exclusive(self, value):
        if (value <= self.min_exclusive):
            raise ValueError(
                generate_error_message(
                    _("Value {0} is bellow or equal lower limit : {1}"),
                    value,
                    self.min_exclusive))

    def check_min_inclusive(self, value):
        if (value < self.min_inclusive):
            raise ValueError(
                generate_error_message(
                    _("Value {0} is bellow the lower limit : {1}"),
                    value,
                    self.min_inclusive))

    def convert(self, value=None):
        try:
            try:
                if(self.data_type == date):
                    return (datetime.strptime(value, self.input_format)
                            .date())

                elif(self.data_type == decimal.Decimal):
                    # TODO need improvement for other input options besides fl
                    if( hasattr (self, 'fl_length') and hasattr( self, 'fraction_digits' ) ):
                        tmp = (
                            value[:self.fl_length - self.fraction_digits]
                            + '.'
                            + value[self.fl_length - self.fraction_digits:]
                        )
                    else:
                        tmp = value
                    return decimal.Decimal(tmp)
            # There is no specific convertion rules, so it just pass
            except AttributeError:
                pass

            if(not(isinstance(value, self.data_type))):
                return(self.data_type(value))
            else:
                return value
        except Exception:
            if( hasattr(self.__class__, 'value_on_error') ):
                try:
                    return(self.data_type(self.value_on_error))
                except Exception as e :
                    raise Exception(
                        generate_error_message(
                            _("Can't convert value {0} neither "
                                "value_on_error  {1} to {2} data type"
                                "in {3}"),
                                value,
                                self.value_on_error,
                                self.data_type, 
                                str( self )
                            )
                    ) from e
                except Exception as e :
                    raise Exception(
                    generate_error_message(
                        _("Can't convert value {0} to {1} data type"
                            " in {2}"),
                            value,
                            self.data_type, 
                            str( self )
                        )
                ) from e
    def process_white_spaces(self, value):
        if(isinstance(value, str)):
            if(self.white_space_behaviour
                    == WhiteSpaceBehaviour.REPLACE
               ):
                return re.sub('\s', ' ', value)
            elif(self.white_space_behaviour
                    == WhiteSpaceBehaviour.COLLAPSE
                 ):
                value = value.strip()
                return re.sub('\s+', ' ', value)
        return value

    def __unicode__(self):
        tmp = str(vars(self))
        return tmp

    def __repr__(self):
        return self.__unicode__()


def generate_error_message(*args):
    # ~ arg_list=list( args )
    raise ValueError(args[0].format(*args[1:]))


def data_property(
        fget=None,
        length=None,
        min_length=None,
        max_length=None,
        valid_values=None,
        pattern=None,
        max_exclusive=None,
        max_inclusive=None,
        min_exclusive=None,
        min_inclusive=None,
        data_type=None,
        value_on_error=None,
        white_space_behaviour=None,
        sql_column_type=Sql.ColumnType.SIMPLE,
        allow_none=None,
        total_digits=None,
        fraction_digits=None,
        default_value=None,
        fl_start=None,
        fl_length=None,
        input_format=None,
        csv_position=None):
    if(fget is None):
        def wrapper(fget):
            return DataProperty(
                fget=fget,
                length=length,
                min_length=min_length,
                max_length=max_length,
                valid_values=valid_values,
                pattern=pattern,
                max_exclusive=max_exclusive,
                max_inclusive=max_inclusive,
                min_exclusive=min_exclusive,
                min_inclusive=min_inclusive,
                data_type=data_type,
                value_on_error=value_on_error,
                white_space_behaviour=white_space_behaviour,
                sql_column_type=sql_column_type,
                allow_none=allow_none,
                total_digits=total_digits,
                fraction_digits=fraction_digits,
                default_value=default_value,
                fl_start=fl_start,
                fl_length=fl_length,
                input_format=input_format,
                csv_position=csv_position)
        return wrapper
    else:
        return DataProperty(fget=fget)


def auto_data_property(
        place_holder_function=None,
        length=None,
        min_length=None,
        max_length=None,
        valid_values=None,
        pattern=None,
        max_exclusive=None,
        max_inclusive=None,
        min_exclusive=None,
        min_inclusive=None,
        data_type=None,
        value_on_error=None,
        white_space_behaviour=None,
        sql_column_type=Sql.ColumnType.SIMPLE,
        allow_none=None,
        total_digits=None,
        fraction_digits=None,
        default_value=None,
        fl_start=None,
        fl_length=None,
        input_format=None,
        csv_position=None):
    if(place_holder_function is None):
        def wrapper(place_holder_function):
            return DataProperty(
                place_holder_function=place_holder_function,
                length=length,
                min_length=min_length,
                max_length=max_length,
                valid_values=valid_values,
                pattern=pattern,
                max_exclusive=max_exclusive,
                max_inclusive=max_inclusive,
                min_exclusive=min_exclusive,
                min_inclusive=min_inclusive,
                data_type=data_type,
                value_on_error=value_on_error,
                white_space_behaviour=white_space_behaviour,
                sql_column_type=sql_column_type,
                allow_none=allow_none,
                total_digits=total_digits,
                fraction_digits=fraction_digits,
                default_value=default_value,
                fl_start=fl_start,
                fl_length=fl_length,
                input_format=input_format,
                csv_position=csv_position)
        return wrapper
    else:
        return DataProperty(
            place_holder_function=place_holder_function)
