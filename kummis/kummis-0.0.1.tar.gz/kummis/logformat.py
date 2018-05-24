import logging
from datetime import datetime

from typing import Dict
from typing import Any

import ujson


class KumparanLoggingFormatter(logging.Formatter):
    """
    KumparanLoggingFormatter instances are used to convert a LogRecord
    to JSON-formatted string.
    Example usage:
        handler = logging.StreamHandler(stream=sys.stdout)
        formatter = StackdriverLoggingFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    """
    def __init__(self, service_name=None, service_version=None, environment=None):
        logging.Formatter.__init__(self)

        self.service_context = None
        if service_name or service_version:
            self.service_context = {
                "service": service_name,
                "version": service_version,
                "environment": environment
            }

    def formatTime(self,
                   record: logging.LogRecord,
                   datefmt: str = None) -> str:
        """
        formatTime formats LogRecord.created seconds in readable UTC format.
        """
        seconds = record.created
        # nanoseconds = seconds * 1e9
        current_time = datetime.utcfromtimestamp(seconds)
        s = current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return s

    def format(self, record: logging.LogRecord) -> str:
        # Collect a LogRecord as python dictionary
        log_record: Dict[str, Any] = {}
        log_record["timestamp"] = self.formatTime(record)
        log_record["severity"] = record.levelname
        log_record["message"] = record.getMessage()
        log_record["sourceLocation"] = {
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
        }
        # Handle exception information
        if record.exc_info:
            traceback = self.formatException(record.exc_info)
            # Append the traceback as a newline
            log_record["message"] += "\n{}".format(traceback)

        # Add service context to log record
        if self.service_context:
            log_record["serviceContext"] = self.service_context

        json_str = ujson.dumps(log_record, ensure_ascii=False)
        return json_str