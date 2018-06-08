# coding: utf-8
from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *

import atexit
import contextlib
import logging
import sys
import textwrap
import zmq

from collections import Iterable
from ctypes import *
from enum import Enum
from six import string_types

from . import tecrpc
from .tecrpc.ArgListItem import *
from .tecrpc.Argument import *
from .tecrpc.ArgumentType import *
from .tecrpc.Header import *
from .tecrpc.Message import *
from .tecrpc.OperationType import *
from .tecrpc.Reply import *
from .tecrpc.Request import *
from .tecrpc.Status import *
import flatbuffers
from flatbuffers import number_types as N

from ..constant import *
from ..exception import *
from .tecutil_rpc import TecUtilRPC, ValueType

from . import patch_flatbuffers


log = logging.getLogger(__name__)


def Int8Array(self, j=None):
    return self._tab.GetVector(30, c_int8, j)


def Uint8Array(self, j=None):
    return self._tab.GetVector(32, c_uint8, j)


def Int16Array(self, j=None):
    return self._tab.GetVector(34, c_int16, j)


def Uint16Array(self, j=None):
    return self._tab.GetVector(36, c_uint16, j)


def Int32Array(self, j=None):
    return self._tab.GetVector(38, c_int32, j)


def Uint32Array(self, j=None):
    return self._tab.GetVector(40, c_uint32, j)


def Int64Array(self, j=None):
    return self._tab.GetVector(42, c_int64, j)


def Uint64Array(self, j=None):
    return self._tab.GetVector(44, c_uint64, j)


def Float32Array(self, j=None):
    return self._tab.GetVector(46, c_float, j)


def Float64Array(self, j=None):
    return self._tab.GetVector(48, c_double, j)


tecrpc.Argument.Argument.Int8Array = Int8Array
tecrpc.Argument.Argument.Uint8Array = Uint8Array
tecrpc.Argument.Argument.Int16Array = Int16Array
tecrpc.Argument.Argument.Uint16Array = Uint16Array
tecrpc.Argument.Argument.Int32Array = Int32Array
tecrpc.Argument.Argument.Uint32Array = Uint32Array
tecrpc.Argument.Argument.Int64Array = Int64Array
tecrpc.Argument.Argument.Uint64Array = Uint64Array
tecrpc.Argument.Argument.Float32Array = Float32Array
tecrpc.Argument.Argument.Float64Array = Float64Array


def build_arglist_item(builder, key, val):
    assert isinstance(key, string_types) or isinstance(key, c_char)

    if isinstance(key, c_char):
        key = key.value.decode('utf-8')

    key = builder.CreateString(key)

    if isinstance(val, tecplot.tecutil.StringList):
        addr = getattr(val, 'value', val)
        value = build_address_arg(builder, ArgumentType.StringList, addr)
    elif isinstance(val, tecplot.tecutil.IndexSet):
        addr = getattr(val, 'value', val)
        value = build_address_arg(builder, ArgumentType.IndexSet, addr)
    elif isinstance(val, string_types):
        value = build_text_arg(builder, None, val)
    elif isinstance(val, (float, c_double)):
        value = build_scalar_arg(builder, c_double, val)

    elif isinstance(val, POINTER(c_double)):  # POSSIBLY IN/OUTPUT
        ArgumentStart(builder)
        ArgumentAddType(builder, ArgumentType.Address | ArgumentType.Float64)
        ArgumentAddFloat64Value(builder, val[0])
        value = ArgumentEnd(builder)

    elif isinstance(val, (int, bool)):
        value = build_scalar_arg(builder, c_int64, val)
    elif isinstance(val, Enum):
        value = build_scalar_arg(builder, c_int64, val.value)

    elif isinstance(val, c_size_t):  # POSSIBLY IN/OUTPUT
        value = build_arbparam_arg(builder, None, val)
    elif isinstance(val, POINTER(c_size_t)):  # POSSIBLY IN/OUTPUT
        ptr = cast(val, c_void_p)
        value = build_arbparam_arg(builder, POINTER, ptr.value)
    elif isinstance(val, POINTER(POINTER(c_char))):  # POSSIBLY IN/OUTPUT
        value = build_arbparam_arg(builder, POINTER, val.contents)
    elif isinstance(val, POINTER(c_char_p)):  # POSSIBLY IN/OUTPUT
        value = build_text_arg(builder, ArgumentType.Address, val)

    else:
        if isinstance(val, Iterable):
            val = list(val)
        if isinstance(val, list):
            if isinstance(val[0], Enum):
                enum_values = [e.value for e in val]
                value = build_array_arg(builder, c_int32, enum_values)
            elif isinstance(val[0], float):
                value = build_array_arg(builder, c_double, val)
            elif len(val) == 0 or isinstance(val[0],int):
                value = build_array_arg(builder, c_int64, val)
            else:
                msg = 'invalid type: {} ({} = {})'
                msg = msg.format(type(val),key,val)
                raise TecplotTypeError(msg)
        else:
            msg = 'invalid type: {} ({} = {})'
            msg = msg.format(type(val),key,val)
            raise TecplotTypeError(msg)

    ArgListItemStart(builder)
    ArgListItemAddKey(builder, key)
    ArgListItemAddValue(builder, value)
    return ArgListItemEnd(builder)


def build_arglist_arg(builder, arglist):
    assert isinstance(arglist, tecplot.tecutil.LocalArgList)

    ArgumentStart(builder)
    ArgumentAddType(builder, ArgumentType.ArgList)
    arg = ArgumentEnd(builder)

    items = []
    for key, val in arglist.items():
        items.append(build_arglist_item(builder, key, val))
    RequestStartArglistVector(builder, len(items))
    for item in reversed(items):
        builder.PrependUOffsetTRelative(item)
    argList = builder.EndVector(len(items))

    return arg, argList


def build_address_arg(builder, argtype, arg):
    assert argtype in [c_uint64, ArgumentType.StringList, ArgumentType.IndexSet]

    if argtype is c_uint64:
        argtype = ArgumentType.Address
    elif not argtype & ArgumentType.Address:
        argtype |= ArgumentType.Address

    ArgumentStart(builder)
    if arg is None or arg == 0 or argtype & ArgumentType.Null:
        ArgumentAddType(builder, argtype | ArgumentType.Null)
    else:
        ArgumentAddType(builder, argtype)
        ArgumentAddUint64Value(builder, arg)
    return ArgumentEnd(builder)


def build_arbparam_arg(builder, argtype, arg):
    assert argtype in [None, POINTER, ArgumentType.Address]
    if isinstance(arg, POINTER(c_char)):
        arg = cast(arg, c_char_p).value.decode('utf-8')
    is_addr = argtype is not None and (argtype is POINTER or
                                       argtype & ArgumentType.Address)
    if isinstance(arg, string_types):
        t = ArgumentType.ArbParam | ArgumentType.Text
        if is_addr:
            t |= ArgumentType.Address
        a = builder.CreateString(arg or '')
        ArgumentStart(builder)
        ArgumentAddType(builder, t)
        ArgumentAddText(builder, a)
    else:
        ArgumentStart(builder)
        if is_addr:
            t = ArgumentType.ArbParam | ArgumentType.Address
            ArgumentAddType(builder, t)
            ArgumentAddUint64Value(builder, arg)
        elif isinstance(arg, Enum):
            ArgumentAddType(builder, ArgumentType.ArbParam | ArgumentType.Enum)
            ArgumentAddInt64Value(builder, arg.value)
        else:
            i = int(getattr(arg, 'value', arg))
            ArgumentAddType(builder, ArgumentType.ArbParam)
            ArgumentAddInt64Value(builder, c_int64(i).value)
    return ArgumentEnd(builder)


def build_array_arg(builder, argtype, arg):
    _types = {
        c_bool: ArgumentType.Bool,
        c_uint8: ArgumentType.UInt8,
        c_uint32: ArgumentType.UInt32,
        c_uint64: ArgumentType.UInt64,
        c_int32: ArgumentType.Int32,
        c_int64: ArgumentType.Int64,
        c_float: ArgumentType.Float32,
        c_double: ArgumentType.Float64}
    if arg is None:
        t = ArgumentType.Unspecified if argtype is None else _types[argtype]
        t |= ArgumentType.Array | ArgumentType.Null
        ArgumentStart(builder)
        ArgumentAddType(builder, t)
    else:
        if argtype is None:
            t = ArgumentType.Array
            try:
                t |= _types[arg._type_]
            except KeyError:
                t |= ArgumentType.Unspecified
            ArgumentStart(builder)
            ArgumentAddType(builder, t)
            ArgumentAddUint64Value(builder, len(arg))
        else:
            _dispatch = {
                ArgumentType.UInt8: ArgumentAddUint8Array,
                ArgumentType.UInt32: ArgumentAddUint32Array,
                ArgumentType.UInt64: ArgumentAddUint64Array,
                ArgumentType.Int32: ArgumentAddInt32Array,
                ArgumentType.Int64: ArgumentAddInt64Array,
                ArgumentType.Float32: ArgumentAddFloat32Array,
                ArgumentType.Float64: ArgumentAddFloat64Array,}
            arr = builder.CreateVector(argtype, arg)
            ArgumentStart(builder)
            ArgumentAddType(builder, ArgumentType.Array | _types[argtype])
            ArgumentAddUint64Value(builder, len(arg))
            _dispatch[_types[argtype]](builder, arr)
    return ArgumentEnd(builder)


def build_scalar_arg(builder, argtype, arg):
    _types = {
        c_bool: ArgumentType.Bool,
        c_uint8: ArgumentType.UInt8,
        c_uint32: ArgumentType.UInt32,
        c_uint64: ArgumentType.UInt64,
        c_int32: ArgumentType.Int32,
        c_int64: ArgumentType.Int64,
        c_float: ArgumentType.Float32,
        c_double: ArgumentType.Float64,}
    _dispatch = {
        ArgumentType.Bool: ArgumentAddBoolean,
        ArgumentType.UInt8: ArgumentAddUint8Value,
        ArgumentType.UInt32: ArgumentAddUint32Value,
        ArgumentType.UInt64: ArgumentAddUint64Value,
        ArgumentType.Int32: ArgumentAddInt32Value,
        ArgumentType.Int64: ArgumentAddInt64Value,
        ArgumentType.Float32: ArgumentAddFloat32Value,
        ArgumentType.Float64: ArgumentAddFloat64Value,}
    t = _types[argtype]
    ArgumentStart(builder)
    ArgumentAddType(builder, t)
    _dispatch[t](builder, arg)
    return ArgumentEnd(builder)


def build_text_arg(builder, argtype, arg):
    assert argtype in [None, ArgumentType.Address]
    if isinstance(arg, c_char):
        arg = arg.value.decode('utf-8')
    t = ArgumentType.Text
    if argtype is not None and argtype & ArgumentType.Address:
        t |= ArgumentType.Address
    if arg is None:
        ArgumentStart(builder)
        ArgumentAddType(builder, t | ArgumentType.Null)
    else:
        a = builder.CreateString(arg or '')
        ArgumentStart(builder)
        ArgumentAddText(builder, a)
        ArgumentAddType(builder, t)
    return ArgumentEnd(builder)


def build_args(builder, *args):
    _dispatch = {
        ValueType.Address: build_address_arg,
        ValueType.ArbParam: build_arbparam_arg,
        ValueType.Array: build_array_arg,
        ValueType.Scalar: build_scalar_arg,
        ValueType.Text: build_text_arg,}

    reqargs = []
    arglist = None
    for valtype, argtype, arg in args:
        if isinstance(arg, tecplot.tecutil.LocalArgList):
            assert argtype is c_uint64
            reqarg, arglist = build_arglist_arg(builder, arg)
            reqargs.append(reqarg)
        else:
            reqargs.append(_dispatch[valtype](builder, argtype, arg))

    RequestStartArgsVector(builder, len(reqargs))
    for arg in reversed(reqargs):
        builder.PrependUOffsetTRelative(arg)
    argsvec = builder.EndVector(len(reqargs))

    return argsvec, arglist


def build_finish(builder, optype, opname, args, arglist):
    RequestStart(builder)
    RequestAddType(builder, optype)
    RequestAddOperation(builder, opname)
    RequestAddArgs(builder, args)
    if arglist is not None:
        RequestAddArglist(builder, arglist)
    request = RequestEnd(builder)

    MessageStart(builder)
    MessageAddRequest(builder, request)
    reqmsg = MessageEnd(builder)

    builder.Finish(reqmsg)


def build_tecutil_request(builder, tecutil_command, *args, **kwargs):
    lock = kwargs.pop('lock', True)
    if any(isinstance(a[2], tecplot.tecutil.LocalArgList) for a in args):
        optype = OperationType.TecUtilX
    else:
        optype = OperationType.TecUtil

    if lock:
        optype |= OperationType.LockRequired

    opname = builder.CreateString(tecutil_command)
    reqargs, reqarglist = build_args(builder, *args)
    build_finish(builder, optype, opname, reqargs, reqarglist)

    return optype


class TecUtilClient(TecUtilRPC):
    def __init__(self):
        self.socket = None
        self.tuserver_version = 0
        self.suspended = False
        self.state_changes = {}

    def connect(self, host='localhost', port=7600, timeout=10, quiet=False):
        # Prepare the ZeroMQ context
        self._context = zmq.Context()

        # Setup the request server socket
        self.socket = self._context.socket(zmq.REQ)

        # Set high water mark for out-going messages.
        # This is the maximum number of messages to
        # store in the out-going queue - send() will
        # block until the HWM is below this limit.
        self.socket.setsockopt(zmq.SNDHWM, 10)

        # Do not linger once socket is closed.
        # Send messages immediately, and possibly
        # fail, but do not attempt to recover.
        self.socket.setsockopt(zmq.LINGER, 0)

        # Connect requester to the reply sever
        self.endpoint = "tcp://{host}:{port}".format(host=host, port=port)
        self.socket.connect(self.endpoint)

        self.wait_for_connection(timeout, quiet)

        if self.connected:
            atexit.register(self.disconnect)

        # Bring in tecplot module only on connection to avoid circular deps
        import tecplot
        globals()['tecplot'] = tecplot

    def wait_for_connection(self, timeout=10, quiet=False):

        def post_message(msg, quiet=quiet):
            if not quiet:
                if log.getEffectiveLevel() <= logging.INFO:
                    log.info(msg)
                else:
                    print(msg)

        post_message(
            'Connecting to Tecplot 360 TecUtil Server on:\n    {}'.format(
                self.endpoint))

        if not self.is_server_listening(timeout):
            self.disconnect()
            raise TecplotTimeoutError('Failed to connect to TecUtil Server.')

        post_message('Connection established.')

    def is_server_listening(self, timeout=10):
        if self.socket is None:
            raise TecplotLogicError('Not connected to Tecplot 360.')

        builder = flatbuffers.Builder(0)
        opname = builder.CreateString('UTHR?')
        RequestStart(builder)
        RequestAddType(builder, OperationType.Server)
        RequestAddOperation(builder, opname)
        request = RequestEnd(builder)
        MessageStart(builder)
        MessageAddRequest(builder, request)
        reqmsg = MessageEnd(builder)
        builder.Finish(reqmsg)

        self.socket.send(builder.Output())

        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)
        if poller.poll(timeout * 1000):
            msg = self.socket.recv()
            repmsg = Message.GetRootAsMessage(msg, 0)
            if repmsg.Reply().Status() == Status.Success:
                try:
                    self.tuserver_version = repmsg.Header().TuserverVersion()
                except AttributeError:
                    self.tuserver_version = 0
                return True

        return False

    @property
    def connected(self):
        return self.socket is not None

    def disconnect(self):
        if self.socket:
            if sys.version_info >= (3,):
                atexit.unregister(self.disconnect)
            self.socket.disconnect(self.endpoint)
            self.socket = None
            self.tuserver_version = 0

    def sndrcv(self, tecutil_command, *args, **kwargs):
        builder = flatbuffers.Builder(0)
        optype = build_tecutil_request(builder, tecutil_command, *args,
                                       **kwargs)
        self.socket.send(builder.Output())
        reply_message = self.socket.recv()
        reply = Message.GetRootAsMessage(reply_message, 0)

        if optype & OperationType.TecUtilX:
            reply = self.read_tecutilx_reply(args, reply)

        return reply

    def chk(self, reply):
        if reply.Status() != Status.Success:
            errmsg = reply.Log()
            if not isinstance(errmsg, string_types):
                errmsg = errmsg.decode('utf-8')
            raise TecplotSystemError(errmsg)

    def read_arbparam(self, arg):
        T = ArgumentType
        t = arg.Type()
        if t & (T.Unspecified | T.Address):
            return arg.Int64Value()
        elif t & T.Null:
            return None
        elif t & T.Text:
            txt = arg.Text()
            if isinstance(txt, string_types):
                txt = cast(c_char_p(txt), POINTER(c_char))
            else:
                txt = cast(pointer(create_string_buffer(txt)), POINTER(c_char))
            return txt
        else:
            TecplotNotImplementedError

    def read_text(self, arg):
        T = ArgumentType
        t = arg.Type()
        if t & (T.Unspecified | T.Text):
            txt = arg.Text()
            try:
                txt = txt.decode('utf-8')
            except AttributeError:
                pass
            return txt
        elif t & T.Null:
            return None
        else:
            TecplotNotImplementedError

    def read_ptr(self, arg):
        return arg.Uint64Value()

    def read_array(self, arg, argtype):
        _dispatch = {
            c_uint8: arg.Uint8Array,
            c_int8: arg.Int8Array,
        }
        return _dispatch[argtype]()

    def read_tecutilx_reply(self, args, msg):
        for valtype, argtype, arg in args:
            if isinstance(arg, tecplot.tecutil.LocalArgList):
                reply = msg.Reply()

                for i in range(reply.ArglistLength()):
                    item = reply.Arglist(i)
                    key = item.Key().decode('utf-8')
                    value = item.Value()
                    if value.Type() & ArgumentType.Float64:
                        arg[key][0] = value.Float64Value()
                    elif value.Type() & ArgumentType.ArbParam:
                        if value.Type() & ArgumentType.Text:
                            txt = value.Text()
                            if isinstance(txt, string_types):
                                txt = cast(c_char_p(txt), POINTER(c_char))
                            else:
                                txt = cast(txt, POINTER(c_char))
                            arg[key][0] = txt
                        else:
                            arg[key][0] = self.read_arbparam(value)
                    elif value.Type() & ArgumentType.Text:
                        arg[key] = self.read_text(value)
                    else:
                        raise TecplotValueError(key)
        return msg

    @contextlib.contextmanager
    def suspended_interface(self):
        def _send_suspend_interface(suspend=True):
            builder = flatbuffers.Builder(0)

            opname = builder.CreateString('Suspend Interface')

            ArgumentStart(builder)
            ArgumentAddBoolean(builder, suspend)
            arg = ArgumentEnd(builder)

            RequestStartArgsVector(builder, 1)
            builder.PrependUOffsetTRelative(arg)
            argvec = builder.EndVector(1)

            RequestStart(builder)
            RequestAddType(builder, OperationType.Server)
            RequestAddOperation(builder, opname)
            RequestAddArgs(builder, argvec)
            request = RequestEnd(builder)

            MessageStart(builder)
            MessageAddRequest(builder, request)
            reqmsg = MessageEnd(builder)
            builder.Finish(reqmsg)

            self.socket.send(builder.Output())
            reply_message = self.socket.recv()
            reply = Message.GetRootAsMessage(reply_message, 0)
            self.chk(reply.Reply())

        assert self.socket is not None

        if self.tuserver_version < 2:
            log.warn('This version of the TecUtil Server addon does not'
                     ' support the suspended interface context. Please update'
                     ' to the newest version of Tecplot 360.')
            yield
        else:
            if self.suspended:
                yield
            else:
                try:
                    _send_suspend_interface(True)
                    self.suspended = True
                    yield
                finally:
                    self.suspended = False
                    _send_suspend_interface(False)
