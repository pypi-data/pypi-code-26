import os


class Store(object):
    def __init__(self):
        raise TypeError('This class should not be initialized')

    config_id = os.environ.get('CONFIGURATION_ID')

    if os.environ.get('SEC_REFRESH_TOKEN'):
        token = os.environ['SEC_REFRESH_TOKEN']
    else:
        token = None

    performance_id = os.environ.get('PERFORMANCE_ID')

    token_data = dict()

    host = os.environ.get('HOST', 'https://shortesttrack.com')
