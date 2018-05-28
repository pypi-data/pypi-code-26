import argparse
import logging
import signal
import sys

logger = logging.getLogger(__name__)


def cli_app(**kwargs):
    def decorator(func):
        return CommandLineApp(func, **kwargs)
    return decorator


class CommandLineApp(object):
    """basic cli functionality.

    inspired by `pyCLI`.

    provides:
    - `argparser` and parsed `args`
    - logging helper
    - `SIGTERM` and `KeyboardInterrupt` handling
    - exit handling
    """
    args = None
    argparser = None
    _main = None
    name = None
    exit = None

    def __init__(self, main, name=sys.argv[0], exit_handler=sys.exit, sigterm_handler=None):
        self._main = main
        self.name = name
        self.exit = exit_handler
        self.argparser = argparse.ArgumentParser()
        if sigterm_handler is not False:
            signal.signal(signal.SIGTERM, sigterm_handler or (lambda signal, frame: self.exit('Terminated')))

    def __call__(self):
        self.args = self.argparser.parse_args()
        try:
            self._main(self)
        except KeyboardInterrupt:
            self.exit('KeyboardInterrupt')
        except Exception as e:
            logger.exception(e)
            self.exit('uncaught exception')
        self.exit()

    def init_logger(self, log_level=0):
        """increase log level.

        :param log_level int: `0` - warning, `1` - info, `2` - debug
        :return: None
        """
        if log_level == 0:
            level = logging.WARNING
        elif log_level == 1:
            level = logging.INFO
        else:
            level = logging.DEBUG
        logging.basicConfig(level=level)
