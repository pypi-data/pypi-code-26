import os
import argparse

# Keeper of the config, meant to be private, use get() instead
_config_data = {}


# This class extends argparse to also support environment variables
class EnvDefault(argparse.Action):
    def __init__(self, env_var, required=True, default=None, **kwargs):
        if not default and env_var:
            if env_var in os.environ:
                default = os.environ[env_var]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(
            default=default,
            required=required,
            **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def init(cfg_in):
    global _config_data

    # Ensure required level one keys exist
    if "parser" not in cfg_in:
        cfg_in["parser"] = {}
    if "args" not in cfg_in:
        cfg_in["args"] = []

    # Create ArgumentParser object, pass in config
    parser = argparse.ArgumentParser(**cfg_in["parser"])

    # For each item in "args", run parser.add_argument()
    for arg_cfg in cfg_in["args"]:
        # Extract name from config arg item
        name = arg_cfg["name"]
        del arg_cfg["name"]
        # If missing env_var, imply it from name. Strip, underscore, uppercase
        if name[:1] == "-" and "env_var" not in arg_cfg:
            env_var = name.strip().strip("-").replace("-", "_").upper()
            arg_cfg["env_var"] = env_var
        # Enabling env var handling only if needed
        if "env_var" in arg_cfg:
            arg_cfg["action"] = EnvDefault
        # Add argument, not that it is configured
        parser.add_argument(name, **arg_cfg)

    # Parse args and save result to file-scoped global variable
    _config_data = vars(parser.parse_args())


def get(key, required=False):
    global _config_data

    # If key not found, raise error or return None, depending if it's required
    if key not in _config_data or _config_data[key] is None:
        if not required:
            return None
        raise KeyError("ERROR, missing required config key: " + key)

    return _config_data[key]


def get_all():
    global _config_data
    return _config_data
