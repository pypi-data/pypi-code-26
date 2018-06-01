import sys
import inspect
import importlib
import pkgutil
import inspect
from .base import GitSource

submodules = [ importlib.import_module(__name__ + '.' + name)
               for _,name,_ in pkgutil.walk_packages(sys.modules[__name__].__path__) ]

source_map = {} #map of source names to source class handlers.

for mod in submodules:
    for name,cls in inspect.getmembers(mod):
        if inspect.isclass(cls) and GitSource in cls.__bases__:
            source_map[name.lower()] = cls