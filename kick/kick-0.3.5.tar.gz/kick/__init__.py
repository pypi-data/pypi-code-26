__version__ = "0.3.5"

import os

from .config import Config, update_config
from .logging import Logger

config = None
logger = None
APP_ENV_NAME = None
TRUE_VALUES = {"true", "1"}


def start(name, config_path=None, config_variant=None, without_daiquiri=None):
    global config, logger, APP_ENV_NAME

    APP_ENV_NAME = name.upper().replace("-", "_").replace(" ", "_")
    config_path = config_path or os.getenv("{}_CONFIG".format(APP_ENV_NAME), None)
    config_variant = config_variant or os.getenv(
        "{}_ENV".format(APP_ENV_NAME)
    ) or "config"
    if without_daiquiri is None:
        without_daiquiri = os.getenv(
            "{}_NO_DAIQUIRI".format(APP_ENV_NAME)
        ) in TRUE_VALUES

    config = Config(name, config_path, variant=config_variant)
    logger = Logger(name, without_daiquiri=without_daiquiri)
