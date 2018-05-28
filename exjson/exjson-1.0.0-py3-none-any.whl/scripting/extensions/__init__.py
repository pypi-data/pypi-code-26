import inspect

from scripting.extensions.cryptography import uuidv4, md5, sha1, sha256, sha512
from scripting.extensions.datetime import now, now_add, now_utc, now_utc_add
from scripting.extensions.sequences import sequence

# Functions Dict
# This is ok for now since the list of functions is short. But further refactoring may be required if it grows.
# Warning: When adding functions please do not include the closing parenthesis as seen in existing ones.

_functions = {
    "$.now": now,
    "$.now().add": now_add,
    "$.now().utc": now_utc,
    "$.now().utc().add": now_utc_add,
    "$.uuid": uuidv4,
    "$.md5": md5,
    "$.sha1": sha1,
    "$.sha256": sha256,
    "$.sha512": sha512,
    "$.sequence": sequence
}

def get_function(func_call):
    """Gets an extension function from a raw function call"""
    fn_key = func_call[:func_call.rfind('('):]
    fn_parameters_str = func_call[func_call.rfind('(') + 1:func_call.rfind(')')]
    if fn_parameters_str.strip(' ') == "":
        fn_parameters = []
    else:
        fn_parameters = [remove_quotation(v) for v in fn_parameters_str.split(",")]
    if fn_key in _functions.keys():
        return (_functions[fn_key], fn_parameters)


def remove_quotation(value):
    """Removes quotes from string value"""
    result = value
    if value.strip(' ') != "":
        if value[0] == "\'" or value[0] == "\"":
            result = result[1:]
        if value[-1] == "\'" or value[-1] == "\"":
            result = result[:-1]
    return result


def register_extension_function(name, fn):
    """Register Custom Extension Function"""
    global _functions
    fn_name = f"$.{name}"
    if fn_name in _functions.keys():
        raise Exception(f"Extension Function with name {fn_name} is already registered.")
    else:
        fn_info = inspect.getfullargspec(fn)
        if fn_info.varargs is None:
            raise Exception(f"Provided Extension Function with name {fn_name} does not accept parameters. It must have at least an *arg parameter defined.")
        _functions[fn_name] = fn