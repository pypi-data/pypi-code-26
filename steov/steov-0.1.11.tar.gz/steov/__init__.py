import os
import sys

class Anon:
    def __init__ (self, *dict_args, **dict_kwargs):
        self.__dict__.update(dict(*dict_args, **dict_kwargs))

    def __repr__ (self):
        t = type(self)
        return t.__module__ + "." + t.__name__ + "(" + repr(self.__dict__) + ")"

# http://stackoverflow.com/questions/6086976/how-to-get-a-complete-exception-stack-trace-in-python
def format_exc (additional=0, as_list=False):
    import traceback
    exception_list = traceback.format_stack()[:-(2+additional)]
    ertype, ervalue, tb = sys.exc_info()
    exception_list.extend(traceback.format_tb(tb))
    exception_list.extend(traceback.format_exception_only(ertype, ervalue))
    exception_list.insert(0, "Traceback (most recent call last):\n")
    exception_str = "".join(exception_list)
    if as_list:
        return exception_str.split(os.linesep)[:-1]
    else:
        return exception_str

def noop (*args, **kwargs):
    pass

def identity (self):
    return self
iden = identity

def fread (file):
    with open(file, "rb") as fp:
        return fp.read()
def fwrite (file, data):
    with open(file, "wb") as fp:
        return fp.write(data)
def fappend (file, data):
    with open(file, "ab") as fp:
        return fp.write(data)

def ls (directory):
    for name in os.listdir(directory):
        yield os.path.join(directory, name)

def ls2 (directory):
    for name in os.listdir(directory):
        yield os.path.join(directory, name), name

def inject_logging_trace ():
    import logging
    LOGGING_TRACE_LEVEL = 5
    def logger_trace (self, message, *args, **kwargs):
        if self.isEnabledFor(LOGGING_TRACE_LEVEL):
            self._log(LOGGING_TRACE_LEVEL, message, args, **kwargs)
    logging.addLevelName(LOGGING_TRACE_LEVEL, "TRACE")
    logging.TRACE = LOGGING_TRACE_LEVEL
    logging.Logger.trace = logger_trace
    # TODO Add `logging.trace`. might be equivalent to `rootLogger.trace` ????
    # What even is the root logger? How to get it?
