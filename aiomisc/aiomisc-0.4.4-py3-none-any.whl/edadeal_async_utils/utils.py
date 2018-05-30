import logging
import logging.handlers
import socket
import sys
import traceback
from enum import IntEnum
from functools import wraps, partial
from typing import Iterable, Any

import asyncio
import itertools

from colorlog import ColoredFormatter
from . import fast_json


log = logging.getLogger(__name__)


class LogFormat(IntEnum):
    stream = 0
    json = 1


def threaded(func):
    @wraps(func)
    async def wrap(*args, **kwargs):
        loop = asyncio.get_event_loop()

        return await loop.run_in_executor(
            None, partial(func, *args, **kwargs)
        )

    return wrap


def chunk_list(iterable: Iterable[Any], size: int):
    iterable = iter(iterable)

    item = list(itertools.islice(iterable, size))
    while item:
        yield item
        item = list(itertools.islice(iterable, size))


class JSONLogFormatter(logging.Formatter):
    LEVELS = {
        logging.CRITICAL: "crit",
        logging.FATAL: "fatal",
        logging.ERROR: "error",
        logging.WARNING: "warn",
        logging.WARN: "warn",
        logging.INFO: "info",
        logging.DEBUG: "debug",
        logging.NOTSET: None,
    }

    def format(self, record):
        record.message = record.getMessage()

        data = {}
        for key, value in record.__dict__.items():
            if not key.startswith("_") and value is not None:
                data[key] = value

        data['code_file'] = data.pop('filename')
        data['code_line'] = data.pop('lineno')
        data['code_func'] = data.pop('funcName')

        data['identifier'] = data['name']

        if 'msg' in data:
            data['message_raw'] = data.pop('msg')

        data['code_module'] = data.pop('module')
        data['logger_name'] = data.pop('name')
        data['pid'] = data.pop('process')
        data['proccess_name'] = data.pop('processName')
        data['errno'] = 0 if not record.exc_info else 255
        data['thread_name'] = data.pop('threadName')

        for idx, item in enumerate(data.pop('args', [])):
            data['argument_%d' % idx] = str(item)

        payload = {
            '@fields': data,
            'msg': str(data.pop('message')),
            'level': self.LEVELS[data.pop('levelno')]
        }

        if record.exc_info:
            payload['stackTrace'] = "\n".join(
                traceback.format_exception(*record.exc_info)
            )

        return fast_json.dumps(payload)


def get_logging_handler(log_format: LogFormat=LogFormat.stream):
    if log_format == LogFormat.json:
        formatter = JSONLogFormatter()
        formatter.json_lib = fast_json
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        return handler
    elif log_format == LogFormat.stream:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(ColoredFormatter(
            "%(blue)s[T:%(threadName)s]%(reset)s "
            "%(log_color)s%(levelname)s:%(name)s%(reset)s: "
            "%(message_log_color)s%(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={
                'message': {
                    'WARNING': 'bold',
                    'ERROR': 'bold',
                    'CRITICAL': 'bold',
                },
            },
            style='%'
        ))

        return handler

    raise NotImplementedError


def wrap_logging_handler(handler: logging.Handler,
                         loop: asyncio.AbstractEventLoop=None,
                         buffer_size: int = 1024,
                         flush_interval: float = 0.1):
    loop = loop or asyncio.get_event_loop()

    buffered_handler = logging.handlers.MemoryHandler(
        buffer_size, target=handler
    )

    flush_func = threaded(buffered_handler.flush)

    def flush():
        if not loop.is_running():
            return

        # Looks like a callback hell but this needed for
        # stopping without errors
        task = loop.create_task(flush_func())
        task.add_done_callback(
            lambda *_: loop.call_later(flush_interval, flush)
        )

    loop.call_later(flush_interval, flush)
    return buffered_handler


def configure_logging(log_format: LogFormat=LogFormat.stream,
                      loop: asyncio.AbstractEventLoop=None,
                      buffer_size: int=1024,
                      flush_interval: float=0.1) -> logging.Handler:
    return wrap_logging_handler(
        get_logging_handler(log_format),
        loop=loop,
        buffer_size=buffer_size,
        flush_interval=flush_interval,
    )


def bind_socket(*, address: str, port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(0)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    sock_addr = address, port
    log.info('Listening tcp://%s:%s' % sock_addr)

    try:
        sock.bind(sock_addr)
    finally:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 0)

    return sock
