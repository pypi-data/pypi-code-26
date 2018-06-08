import os.path
import logging.config as logconf

logconf.fileConfig(os.path.join(os.path.dirname(__file__),'..', 'settings','logconf.ini'))
