from __future__ import unicode_literals
from builtins import super, int

from collections import OrderedDict, Iterable, namedtuple
from enum import Enum
from six import string_types
from ctypes import (c_char, c_char_p, c_double, c_int, c_int64, c_size_t,
                    c_void_p, byref, cast, pointer, POINTER)

from .tecutil_connector import _tecutil
from ..exception import *
from .. import version
from ..constant import ArgListArgType
from .stringlist import StringList
from .index_set import IndexSet


class RemoteArgList(c_void_p):
    """Dict-like object holding string,object pairs."""
    def __init__(self, *args, **kwargs):
        super().__init__(_tecutil.ArgListAlloc())
        self._handles = {}
        self._nargs = 0
        for a in args:
            self.update(**a)
        self.update(**kwargs)

    # data access
    def _index(self, key):
        if version.sdk_version_info < (2017, 3):
            for index in range(len(self)):
                if key == self._key(index):
                    return index
        else:
            try:
                success, index = _tecutil.ArgListGetIndexByArgName(self, key)
                if success:
                    return index - 1
            except TecplotSystemError:
                return None

    def _key(self, index):
        return _tecutil.ArgListGetArgNameByIndex(self, index + 1)

    def _type(self, index):
        return ArgListArgType(_tecutil.ArgListGetArgTypeByIndex(self, index+1))

    def _item(self, index):
        get_by_index = {
            ArgListArgType.ArbParam:    _tecutil.ArgListGetArbParamByIndex,
            ArgListArgType.ArbParamPtr: _tecutil.ArgListGetArbParamPtrByIndex,
            ArgListArgType.Array:       _tecutil.ArgListGetArrayByIndex,
            ArgListArgType.Double:      _tecutil.ArgListGetDoubleByIndex,
            ArgListArgType.DoublePtr:   _tecutil.ArgListGetDoublePtrByIndex,
            ArgListArgType.Int:         _tecutil.ArgListGetIntByIndex,
            ArgListArgType.Set:         _tecutil.ArgListGetSetByIndex,
            ArgListArgType.String:      _tecutil.ArgListGetStringByIndex,
            ArgListArgType.StringList:  _tecutil.ArgListGetStringListByIndex,
            ArgListArgType.StringPtr:   _tecutil.ArgListGetStringPtrByIndex,}
        item_type = self._type(index)
        return get_by_index[item_type](self, index + 1)

    def __getitem__(self, key):
        index = self._index(key)
        return self._item(index)

    def __setitem__(self, key, val):
        if __debug__:
            if key in self.keys():
                raise TecplotLogicError('Duplicate ArgList key: '+key)
        # ignore all values set to None.
        if val is None:
            return
        if isinstance(val, StringList):
            self._handles[self._nargs] = val
            _tecutil.ArgListAppendStringList(self, key, val)
        elif isinstance(val, IndexSet):
            self._handles[self._nargs] = val
            _tecutil.ArgListAppendSet(self, key, val)
        elif isinstance(val, string_types):
            _tecutil.ArgListAppendString(self, key, val)
        elif isinstance(val, (float, c_double)):
            _tecutil.ArgListAppendDouble(self, key, val)
        elif isinstance(val, POINTER(c_double)):
            self._handles[self._nargs] = val
            _tecutil.ArgListAppendDoublePtr(self, key, val)
        elif isinstance(val, (int, bool)):
            _tecutil.ArgListAppendInt(self, key, val)
        elif isinstance(val, Enum):
            _tecutil.ArgListAppendInt(self, key, val.value)
        elif isinstance(val, c_size_t):
            _tecutil.ArgListAppendArbParam(self, key,
                cast(byref(val), POINTER(c_int64)).contents)
        elif isinstance(val, POINTER(c_size_t)):
            val = cast(val, POINTER(c_int64))
            self._handles[self._nargs] = val
            _tecutil.ArgListAppendArbParamPtr(self, key, val)
        elif isinstance(val, POINTER(POINTER(c_char))):
            self._handles[self._nargs] = val
            _tecutil.ArgListAppendArbParamPtr(self, key, val)
        elif isinstance(val, POINTER(c_char_p)):
            self._handles[self._nargs] = val
            _tecutil.ArgListAppendStringPtr(self, key, val)
        else:
            if isinstance(val, Iterable):
                val = list(val)
            if isinstance(val, list):
                if isinstance(val[0], Enum):
                    v = (c_int * len(val))(*[e.value for e in val])
                    self._handles[self._nargs] = v
                    _tecutil.ArgListAppendArray(self, key, v)
                elif isinstance(val[0], float):
                    v = (c_double * len(val))(*val)
                    self._handles[self._nargs] = v
                    _tecutil.ArgListAppendArray(self, key, v)
                elif len(val) == 0 or isinstance(val[0],int):
                    v = (c_int64 * len(val))(*val)
                    self._handles[self._nargs] = v
                    _tecutil.ArgListAppendArray(self, key, v)
                else:
                    msg = 'invalid type: {} ({} = {})'
                    msg = msg.format(type(val),key,val)
                    raise TecplotTypeError(msg)
            else:
                msg = 'invalid type: {} ({} = {})'
                msg = msg.format(type(val),key,val)
                raise TecplotTypeError(msg)
        self._nargs += 1

    def __len__(self):
        return _tecutil.ArgListGetArgCount(self)

    def keys(self):
        for index in range(len(self)):
            yield self._key(index)

    def items(self):
        for index, key in enumerate(self.keys()):
            yield key, self._item(index)

    # string representations
    def __repr__(self):
        kwargs = []
        for key, val in self.items():
            kwargs.append("{key}='{val}'".format(key=key, val=val))
        return 'ArgList({kwargs})'.format(kwargs=', '.join(kwargs))

    def __str__(self):
        return str(dict(self))

    # iterating
    def __iter__(self):
        self.current_index = -1
        self.current_length = len(self)
        return self

    def __next__(self):
        self.current_index += 1
        if self.current_index < self.current_length:
            return self._key(self.current_index)
        else:
            del self.current_index
            del self.current_length
            raise StopIteration()

    # context management
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.dealloc()

    # public methods
    def update(self, *args, **kwargs):
        if len(args) > 1:
            msg = 'update expected at most 1 arguments, got ' + len(args)
            raise TypeError(msg)
        if len(args):
            try:
                for k, v in args[0]:
                    if v is not None:
                        self[k] = v
            except TypeError:
                msg = 'arglist update elements require 2 arguments (key, value)'
                raise ValueError(msg)
        for k, v in kwargs.items():
            if v is not None:
                self[k] = v

    def clear(self):
        _tecutil.ArgListClear(self)
        self._handles = {}
        self._nargs = 0

    def dealloc(self):
        _tecutil.ArgListDealloc(pointer(self))
        self._handles = {}
        self._nargs = 0

    def next(self):  # if sys.version_info < (3,)
        return self.__next__()


class LocalArgList(OrderedDict):
    def __setitem__(self, key, val):
        # setting to None deletes existing key
        if val is None:
            if key in self.keys():
                del self[key]
            return

        accepted_types = tuple(list(string_types) + [StringList, IndexSet,
            float, c_double, POINTER(c_double), int, bool, Enum, c_size_t,
            POINTER(c_size_t), POINTER(c_int64), POINTER(POINTER(c_char)),
            POINTER(c_char_p), Iterable])
        if not isinstance(val, accepted_types):
            raise TecplotTypeError(type(val));

        return OrderedDict.__setitem__(self, key, val)

    def __repr__(self):
        kwargs = []
        for key, val in self.items():
            kwargs.append("{key}='{val}'".format(key=key, val=val))
        return 'ArgList({kwargs})'.format(kwargs=', '.join(kwargs))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.clear()

    def dealloc(self):
        self.clear()
