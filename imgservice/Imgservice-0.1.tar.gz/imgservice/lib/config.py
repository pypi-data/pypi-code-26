import os

SKIP = object()


class Option:

    def __init__(self, name, arg_type=str, default=SKIP, var_name=None,
                 required=False):

        self.name = name
        self.arg_type = arg_type
        self.default = default
        self.var_name = var_name or name
        self.required = required

    @classmethod
    def integer(cls, *args, **kwargs):
        kwargs['arg_type'] = int
        return cls(*args, **kwargs)

    @classmethod
    def boolean(cls, *args, **kwargs):
        kwargs['arg_type'] = bool
        return cls(*args, **kwargs)


option = Option


def configure_from_environ(app, options, env=None):
    """Configure a Flask app from the environment

    Args:
        app (Flask):
            flask application to configure
        options:
            list of ``option`` tuples
        env:
            optional dict-like to read the environment from. Defaults
            to ``os.environ``.
    """

    for option in options:
        value = get_from_environment(
            option.var_name, option.arg_type, option.default, env=env)

        if option.required and ((not value) or value is SKIP):
            raise ValueError('Missing required configuration: {}'
                             .format(option.var_name))

        if value is not SKIP:
            app.config[option.name] = value


def get_from_environment(name, arg_type, default, env=None):
    """Get a value from an environment variable

    Args:
        name:
            Environment variable name
        arg_type:
            Type of argument to be read. Callable accepting the raw
            value as single argument and returning the appropriate
            Python object. ``bool`` will be handled in a special case
            (see ``flag_from_string``).
        default:
            Default value to use if the variable is not set.
        env:
            optional dict-like to read the environment from. Defaults
            to ``os.environ``.

    Returns:
        the retrieved value
    """

    if env is None:
        env = os.environ
    if name not in env:
        # Skip the conversion part
        return default
    value = env[name]
    if arg_type is bool:
        return flag_from_string(value)
    return arg_type(value)


def flag_from_string(orig_value):
    """Convert a string to boolean value

    Args:
        orig_value: the string to be converted

    Returns:
        True:
            if orig_value is one of y, yes, t, true, 1, on
        False:
            if orig_value is one of n, no, f, false, 0, off, or the
            empty string

    Raises:
        ValueError: if orig_value is any other string
    """

    value = orig_value.lower()
    TRUTHY = ['y', 'yes', 't', 'true', '1', 'on']
    FALSEY = ['n', 'no', 'f', 'false', '0', 'off', '']
    if value in TRUTHY:
        return True
    if value in FALSEY:
        return False
    raise ValueError('Not a boolean: {}'.format(orig_value))
