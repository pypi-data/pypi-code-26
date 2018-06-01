import logging
import sys


def stdout_handler(fmt=None):
    handler = logging.StreamHandler(sys.stdout)
    if fmt is None:
        fmt = "[%(levelname)s] %(message)s"
    handler.setFormatter(logging.Formatter(fmt=fmt))
    handler.setLevel(logging.INFO)
    return handler


def init(name):
    root_logger = logging.getLogger(name)
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(stdout_handler())
