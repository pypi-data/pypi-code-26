"""Config read and write.

################################################################################
# Modules required
################################################################################
* config_from_path
  - ruamel.yaml
  - trafaret_config
* read_config
  - pyyaml
"""
import os
import sys


def config_from_path(filepath, config_schema=None):
    """Read a config file from a given path.

    Args:
        filepath (str)  :A string representing the full path of your configfile. eg. /mnt/data/myconfig.yaml
        config_schema (trafaret): Trafaret object that defines the schema of the config.
            If None, then trafaret validation is not used.
            Example:
            ```
            import trafaret as tr
            config_schema = tr.Dict({
                tr.Key('project_name'):
                    tr.Dict({
                        'db_path': tr.String(),
                        'username': tr.String(),
                        'password': tr.String(),
                    }),
            })
            ```
            Trafaret docs: http://trafaret.readthedocs.io/en/latest/
    Return:
        config json
    """
    import ruamel.yaml
    from trafaret_config import read_and_validate
    if config_schema is None:
        with open(filepath) as stream:
            config = ruamel.yaml.load(stream, ruamel.yaml.RoundTripLoader)
            return config
    else:
        config = read_and_validate(filepath, config_schema)
        return config


def config_from_env(key, config_schema=None):
    """Read config from a file path in os.env.

    Args:
        key (str)   : Key represents an evironment variable to read config path
        config_schema (trafaret): Trafaret object that defines the schema of the config.
            If None, then trafaret validation is not used.
            Example:
            ```
            import trafaret as tr
            config_schema = tr.Dict({
                tr.Key('project_name'):
                    tr.Dict({
                        'db_path': tr.String(),
                        'username': tr.String(),
                        'password': tr.String(),
                    }),
            })
            ```
            Trafaret docs: http://trafaret.readthedocs.io/en/latest/
    Return:
        config json
    """
    filepath = os.getenv(key, default=None)
    if not filepath:
        sys.stderr.write("Passed key does not exist: {0}".format(key))
        raise AttributeError('Key {} does not exist in environment.'.format(key))

    return config_from_path(filepath, config_schema)


def read_config(config_filename):
    """Read and return config from filename.

    Args:
        config_filename (str): Path to config file
    Returns:
        dict: Config file as a dictionary.
    """
    import yaml
    with open(config_filename, 'r') as f:
        config = yaml.load(f)
    return config
