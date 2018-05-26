import os
import argparse

"""
This helper package wraps argparse, loading config from environment variables
as well as the usual command line arguments / flags. A config object is passed
into init(), configuring argparse. The environment variables are implied from
the arg name (stripped, uppercased and underscored), but can be manually
defined using the key "env_var" in args config. Once args are loaded, config
is accessable using a getter function "get()". To install, save this file as
./config/config.py, and create an empty ./config/__init__.py.

Usage:

from config import config

# Initialize once, pass in config
config.init({
    "parser": {
      "description": "this is the service description"
    },
    "args": [
        {
            "name": "-test",
            "help": "Description of test",
            "required": False,
            "default": "testing",
        }, {
            "name": "--foo",
            "help": "Description of foo",
            "required": True,
        }, {
            "name": "-f",
            "help": "Description of f",
            "required": False,
            "env_var": "LETTER_F",
        }
    ]
})

# Return value of config. If missing, return None
config.get("test")

# Return value of config. If missing, raise KeyError
config.get("test", True)

"""

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
    if key not in _config_data or _config_data[key] == None:
        if not required:
            return None
        raise KeyError("ERROR, missing required config key: " + key)

    return _config_data[key]
