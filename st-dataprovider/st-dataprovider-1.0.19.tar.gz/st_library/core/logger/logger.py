import six

from st_library.utils.api_client import ApiClient
from st_library.utils.helpers.store import Store

MODE_PRINT = 'mode_print'
MODE_SEND = 'mode_send'

LEVEL_DEBUG = 'DEBUG'
LEVEL_INFO = 'INFO'
LEVEL_NOTICE = 'NOTICE'
LEVEL_WARNING = 'WARNING'
LEVEL_ERROR = 'ERROR'
LEVEL_CRITICAL = 'CRITICAL'
LEVEL_ALERT = 'ALERT'
LEVEL_EMERGENCY = 'EMERGENCY'


class Logger(object):
    """
    A Category for log messages

    Methods
    -------
    debug(message='foo', analysis=False)
        Log with DEBUG level

    info(message='foo', analysis=False)
        Log with INFO level

    notice(message='foo', analysis=False)
        Log with NOTICE level

    warning(message='foo', analysis=False)
        Log with WARNING level

    error(message='foo', analysis=False)
        Log with ERROR level

    critical(message='foo', analysis=False)
        Log with CRITICAL level

    alert(message='foo', analysis=False)
        Log with ALERT level

    emergency(message='foo', analysis=False)
        Log with EMERGENCY level

    Notes
    -----

    The target for logging data is depends on the existence of the performance_id for current Environment.
    If performance_id is specified, then all the data will be sent to ST Services.
    Otherwise, it will be just printed to stdout

    Examples
    --------

        >>> from st_library import Library
        >>> st_lib = Library()
        >>> st_lib.logger.info('Script started.')

    """
    def __init__(self):
        self._mode = MODE_SEND if Store.performance_id else MODE_PRINT

    def _format_message(self, message, level):
        return '{level}: {message}'.format(level=level, message=message)

    def _log(self, message, analysis, level):
        if self._mode == MODE_SEND:
            payload = {
                'level': level,
                'analysis': analysis,
                'data': message
            }
            ApiClient.post(ApiClient.res.logging_post(Store.performance_id), json=payload, raw_response=True)
        else:
            six.print_(self._format_message(message, level))

    def debug(self, message, analysis=False):
        self._log(message, analysis, LEVEL_DEBUG)

    def info(self, message, analysis=False):
        self._log(message, analysis, LEVEL_INFO)

    def notice(self, message, analysis=False):
        self._log(message, analysis, LEVEL_NOTICE)

    def warning(self, message, analysis=False):
        self._log(message, analysis, LEVEL_WARNING)

    def error(self, message, analysis=False):
        self._log(message, analysis, LEVEL_ERROR)

    def critical(self, message, analysis=False):
        self._log(message, analysis, LEVEL_CRITICAL)

    def alert(self, message, analysis=False):
        self._log(message, analysis, LEVEL_ALERT)

    def emergency(self, message, analysis=False):
        self._log(message, analysis, LEVEL_EMERGENCY)
