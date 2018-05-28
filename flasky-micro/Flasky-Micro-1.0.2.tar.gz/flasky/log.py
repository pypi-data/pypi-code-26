import os
import yaml
import logging
import logging.config
from .exceptions import FileNotFoundException
from .exceptions import ConfigurationException


root = logging.getLogger("root")
flasky = logging.getLogger("flasky")
http = logging.getLogger("http")


def load_log_configuration(file):
    if not file or not os.path.exists(file):
        raise FileNotFoundException(file)

    try:
        with open(file, "r") as file:
            config = yaml.load(file)
            logging.config.dictConfig(config)
    except Exception as ex:
        raise ConfigurationException(ex)
