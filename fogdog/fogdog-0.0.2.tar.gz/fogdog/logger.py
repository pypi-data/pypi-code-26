import logging


__all__ = ['logger']


# logger
logger = logging.getLogger('fogdog')
# logger level
logger.setLevel(level=logging.INFO)

# logger format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# file handler
logger_file = None
if logger_file:
    file_handler = logging.FileHandler(logger_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


# console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)