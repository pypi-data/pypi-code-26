import logging
from .api import Client, APIError
from .estimator import Classifier, Regressor

api_key = None
logger = logging.getLogger('justml')

def activate_logging(level=logging.INFO, propagate=True):
    logging.basicConfig()
    logger.setLevel(level)
    logger.propagate = propagate

def available_credits():
    client = Client()
    res = client.list('/v1/accounts/')
    account = res[0]
    return account['credits']
