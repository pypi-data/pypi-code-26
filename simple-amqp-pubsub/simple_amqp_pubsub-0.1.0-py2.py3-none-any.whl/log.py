import logging
from os import environ

LOG_LEVEL = environ.get('LOG_LEVEL', 'error')
logger = logging.getLogger('simple_amqp_pubsub')
log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)8s %(name)s - %(message)s',
))
logger.addHandler(log_handler)
logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
