# pylint:disable=W,C,R
from py_rofi_bus.components import Config


class HasConfig(object):

    def __init__(self, config=None, *args,  **kwargs):
        if config is None:
            self.config = Config(*args,  **kwargs)
        else:
            self.config = config
