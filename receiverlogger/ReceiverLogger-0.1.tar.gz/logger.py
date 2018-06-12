import os
import logging
import logging.handlers

class ContextFilter(logging.Filter):
  def filter(self, record):
    record.msg = record.getMessage()
    return True


class SocketLogger:

  def __init__(self, logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    socket_handler = logging.handlers.SocketHandler('localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    socket_handler.setLevel(logging.DEBUG)
    logger.addHandler(socket_handler)
    self.logger = logger

  def get_logger(self):
    return self.logger


logger = SocketLogger(logger_name='app1').get_logger()