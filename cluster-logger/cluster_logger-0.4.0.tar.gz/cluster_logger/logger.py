# -*- coding: utf-8 -*-
"""Logger that will handle calling logging through different interfaces.

i.e fluentd, HTTP, or whatever comes later.
"""

import logging
from fluent import handler
from .config_builder import ConfigBuilder, FileAccessWrapper


class WrappedLogger:

    logger = None

    def __init__(self, **kwargs):
        self.logger = kwargs.pop('logger', self.logger)

        if not self.logger or not hasattr(self.logger, 'log'):
            raise TypeError(
                'Subclasses must specify a logger, not {}'
                .format(type(self.logger))
            )

        self.extras = kwargs

    def log(self, level, message, *args, **kwargs):
        if isinstance(message, str):
            message = {'message': message}
        message.update(self.extras)

        self.logger.log(level, message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        return self.log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        return self.log(logging.INFO, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        return self.log(logging.WARNING, message, *args, **kwargs)

    warn = warning

    def error(self, message, *args, **kwargs):
        return self.log(logging.ERROR, message, *args, **kwargs)

    def exception(self, message, *args, **kwargs):
        return self.log(logging.ERROR, message, *args, exc_info=1, **kwargs)

    def critical(self, message, *args, **kwargs):
        return self.log(logging.CRITICAL, message, *args, **kwargs)


class ClusterLogger(WrappedLogger):

    custom_format = {
        'level': '%(levelname)s',
        'stack_trace': '%(exc_text)s'
    }

    tag = ''
    fluent_host = 'localhost'
    fluent_port = 24224
    config = {}

    def __init__(self, name: str,):
        """Init the ClusterLogger."""
        self.logger = logging.getLogger(name)
        h = handler.FluentHandler(ClusterLogger.tag,
                                  ClusterLogger.fluent_host,
                                  ClusterLogger.fluent_port)
        formatter = handler.FluentRecordFormatter(ClusterLogger.custom_format)
        h.setFormatter(formatter)
        self.logger.addHandler(h)
        super(ClusterLogger, self).__init__(**ClusterLogger.config)

    @classmethod
    def fromConfig(cls,
                   project: str,
                   application: str,
                   host='fluentd',
                   port=24224,
                   path='',
                   env_keys=[],
                   properties={},):
        """Init config variables."""
        cls.config = ConfigBuilder(FileAccessWrapper(path), env_keys, properties).config
        cls.tag = project + '.' + application
        cls.fluent_host = host
        cls.fluent_port = port

    def log(self, level, message, *args, **kwargs):
        super(ClusterLogger, self).log(level, message, *args, **kwargs)
