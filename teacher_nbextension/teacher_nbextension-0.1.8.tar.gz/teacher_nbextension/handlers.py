import json
import logging
import logging.config
import os

from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join

logger = logging.getLogger(__name__)

# load config from file
# logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
# or, for dictConfig
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'INFO',
            'class':'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(os.path.expanduser("~"), 'jupyter.log'),
        },
        'logstash': {
            'level': 'DEBUG',
            'class': 'logstash.LogstashHandler',
            'host': 'localhost',
            'port': 5959, # Default value: 5959
            'version': 1, # Version of logstash event schema. Default value: 0 (for backward compatibility of the library)
            'message_type': 'logstash',  # 'type' field in logstash message. Default value: 'logstash'.
        }
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file', 'logstash'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
})

class ExecuteHandler(IPythonHandler):
    def get(self):
        self.finish(json.dumps({"response": "ok"}))

    def post(self):
        data = self.request.body_arguments
        formatted = {}

        for k, v in data.items():
            formatted[k] = v
            try:
                v = v[0].decode()
                formatted[k] = v
            except:
                pass
        logger.info(formatted)
        self.finish(json.dumps({"log": "ok"}))


def load_jupyter_server_extension(nb_app):
    nb_app.log.info("Loading the teacher_nbextension serverextension")
    web_app = nb_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], '/execute')
    web_app.add_handlers(host_pattern, [(route_pattern, ExecuteHandler)])
