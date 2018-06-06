""" Utilities to perform multiprotocol single file transfer """

from .core.plugin_manager import PluginManager, ENTRYPOINT_GROUP
__plugin_manager__ = PluginManager()

from .bases.fileutils import FileUtilsBase as FileUtils
from .plugins import __available_plugins__

__plugin_manager__.populate_builtin_plugins(__available_plugins__)
__plugin_manager__.discover_external_plugins()

