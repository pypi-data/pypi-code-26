#!/usr/bin/env python3
# coding: utf-8

"""
    Initialize `logging` Module
    ver. 02 prod

 -----------------------------------------------------------------------------
                                                             hs@uchicago.edu
                                                              April 26, 2018

Initialize `logging` module's configuration for Jupyter notebook or iPython
environment.

Example usage:
    import logging
    from utils import logging_init
"""

import logging
from importlib import reload


FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
# E.g. 
#   12:56 [INFO] Information

DATEFMT = '%H:%M'
# '%d %b %H:%M:%S


def main():
    init_logging()


def init_logging():
    """
    Format logging messages to a nicer layout.

    Initialize the logging level to INFO, log format to `FORMAT`, and date 
    format to `DATEFMT`.
    """
    if in_ipynb():
        # In Jupyter Notebook, `logging` module's `basicConfig()` method
        # only works after reloading.
        reload(logging)

    logging.basicConfig(format=FORMAT, datefmt=DATEFMT, level=logging.INFO)

    info('Initialized logging at INFO level')


def in_ipynb():
    """
    Return True if this code is running in a Jupyter Notebook
    environment.
    """
    try:
        return (str(type(get_ipython()))
                == "<class 'ipykernel.zmqshell.ZMQInteractiveShell'>")
    except NameError:
        return False


def config_logging(level='info', format_=FORMAT, datefmt=DATEFMT):
    """
    Args:
        level (str, in {'debug', 'info', 'warning', 'error', 'critical'}):
    """   
    logging_level_dict = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }
    assert level in logging_level_dict, 'Invalid logging level'

    level_ = logging_level_dict[level]

    reload(logging)
    logging.basicConfig(format=format_, datefmt=datefmt, level=level_)

    # Log a preview message
    logging.log(level_, 'Logging level setted to {}'.format(level.upper()))


def info(*msg_ls, sep=' '):
    """
    """
    msg = printify_logging_msg(msg_ls, sep)
    logging.info(msg)


def printify_logging_msg(msg_ls, sep):
    """
    """
    msg_ls = [str(msg) if not isinstance(msg, str) else msg for msg in msg_ls]
    return sep.join(msg_ls)


def debug(*msg_ls, sep=' '):
    """
    """
    logging.debug(printify_logging_msg(msg_ls, sep))


def warning(*msg_ls, sep=' '):
    """
    """
    logging.warning(printify_logging_msg(msg_ls, sep))


def error(*msg_ls, sep=' '):
    """
    """
    logging.error(printify_logging_msg(msg_ls, sep))


def critical(*msg_ls, sep=' '):
    """
    """
    logging.critical(printify_logging_msg(msg_ls, sep))


main()
