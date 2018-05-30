from scripting.extensions.tools import get_null_value

_SEQUENCE_CACHE = {}


def sequence(*args):
    if len(args) == 0:
        raise AttributeError("Sequence Id most be provided")
    format = None
    if len(args) > 1:
        format = get_null_value(args[1])
    step = 1
    if len(args) > 2:
        step = get_null_value(args[2])
    return _sequence(args[0], format, step)


def _sequence(sequence_key, format=None, step=None):
    global _SEQUENCE_CACHE
    if sequence_key is None or sequence_key == "":
        raise AttributeError("Sequence Id most be provided")
    if sequence_key not in _SEQUENCE_CACHE:
        _SEQUENCE_CACHE[sequence_key] = 0
    if step is None:
        step = 1
    _SEQUENCE_CACHE[sequence_key] += int(step)
    # If format is provided using {0} placeholder apply it
    if format is not None and format != "":
        return format.format(_SEQUENCE_CACHE[sequence_key])
    return _SEQUENCE_CACHE[sequence_key]


def _close_sequences():
    """Resets sequence on dictionary"""
    global _SEQUENCE_CACHE
    for sequence_key in _SEQUENCE_CACHE:
        _SEQUENCE_CACHE[sequence_key] = 0


# Parser will run each call by it self and not evaluate one instance and update all calls with the result
sequence._isolated_instance_execution = True
sequence._close = _close_sequences
