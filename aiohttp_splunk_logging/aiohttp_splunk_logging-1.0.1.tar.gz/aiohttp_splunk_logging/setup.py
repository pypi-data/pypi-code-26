import logging
import time
from .client import SplunkLoggingClient
from .middleware import splunk_requests
from .handler import SplunkHandler

def splunk_my_app(app, splunk_settings):
    app.middlewares.append(splunk_requests)
    app['splunk'] = SplunkLoggingClient(splunk_settings)
    app_logger = logging.getLogger()
    splunk_handler = SplunkHandler(splunk_interface=app['splunk'])
    splunk_handler.setFormatter(logging.Formatter("%(asctime)s"))
    app_logger.addHandler(splunk_handler)
    logging.Formatter.converter = time.gmtime
