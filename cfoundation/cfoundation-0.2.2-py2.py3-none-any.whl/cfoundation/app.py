from .logger import setup_logger
from cement.core.foundation import CementApp
from halo import Halo
from munch import munchify
from os import path
from pydash import _
import inspect
import re

def create_app(name=None, controllers=None, services=None, conf={}):
    src_path = path.dirname(path.abspath((inspect.stack()[1])[1]))
    log = setup_logger(path.join(src_path, 'logger.yml'), name=name)

    def _load_controllers(controllers):
        context = []
        for key in dir(controllers):
            matches = re.findall(r'^(?!Base$)[A-Z].*', key)
            if len(matches) > 0:
                context.append(getattr(controllers, key))
        return context

    class App(CementApp):
        class Meta:
            label = name
            base_controller = controllers.Base
            handlers = _load_controllers(controllers)

        def __init__(self):
            super().__init__()
            self._log = log
            self.conf = munchify(conf)
            self.log = log
            self.services = self.__load_services(services)
            self.spinner = Halo()
            self.src_path = src_path

        def run(self):
            self.log = self._log
            super().run()

        def __load_services(self, services):
            context = Object()
            for key in dir(services):
                matches = re.findall(r'[A-Z].*', key)
                if len(matches) > 0:
                    setattr(context, _.snake_case(key), getattr(services, key)(self))
            return context

    return App

class Object():
    pass
