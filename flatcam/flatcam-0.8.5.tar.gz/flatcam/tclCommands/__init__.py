import pkgutil
import sys

# Todo: I think these imports are not needed.
# allowed command modules (please append them alphabetically ordered)
import flatcam.tclCommands.TclCommandAddCircle
import flatcam.tclCommands.TclCommandAddPolygon
import flatcam.tclCommands.TclCommandAddPolyline
import flatcam.tclCommands.TclCommandAddRectangle
import flatcam.tclCommands.TclCommandAlignDrill
import flatcam.tclCommands.TclCommandAlignDrillGrid
import flatcam.tclCommands.TclCommandCncjob
import flatcam.tclCommands.TclCommandCutout
import flatcam.tclCommands.TclCommandDelete
import flatcam.tclCommands.TclCommandDrillcncjob
import flatcam.tclCommands.TclCommandExportGcode
import flatcam.tclCommands.TclCommandExportSVG
import flatcam.tclCommands.TclCommandExteriors
import flatcam.tclCommands.TclCommandFollow
import flatcam.tclCommands.TclCommandGeoCutout
import flatcam.tclCommands.TclCommandGeoUnion
import flatcam.tclCommands.TclCommandGetNames
import flatcam.tclCommands.TclCommandGetSys
import flatcam.tclCommands.TclCommandImportSvg
import flatcam.tclCommands.TclCommandInteriors
import flatcam.tclCommands.TclCommandIsolate
import flatcam.tclCommands.TclCommandJoinExcellon
import flatcam.tclCommands.TclCommandJoinGeometry
import flatcam.tclCommands.TclCommandListSys
import flatcam.tclCommands.TclCommandMillHoles
import flatcam.tclCommands.TclCommandMirror
import flatcam.tclCommands.TclCommandNew
import flatcam.tclCommands.TclCommandNewGeometry
import flatcam.tclCommands.TclCommandOffset
import flatcam.tclCommands.TclCommandOpenExcellon
import flatcam.tclCommands.TclCommandOpenGCode
import flatcam.tclCommands.TclCommandOpenGerber
import flatcam.tclCommands.TclCommandOpenProject
import flatcam.tclCommands.TclCommandOptions
import flatcam.tclCommands.TclCommandPaint
import flatcam.tclCommands.TclCommandPanelize
import flatcam.tclCommands.TclCommandPlot
import flatcam.tclCommands.TclCommandSaveProject
import flatcam.tclCommands.TclCommandScale
import flatcam.tclCommands.TclCommandSetActive
import flatcam.tclCommands.TclCommandSetSys
import flatcam.tclCommands.TclCommandSubtractPoly
import flatcam.tclCommands.TclCommandSubtractRectangle
import flatcam.tclCommands.TclCommandVersion
import flatcam.tclCommands.TclCommandWriteGCode


__all__ = []

for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(name).load_module(name)
    __all__.append(name)


def register_all_commands(app, commands):
    """
    Static method which registers all known commands.

    Command should  be for now in directory tclCommands and module should start with TCLCommand
    Class  have to follow same  name as module.

    we need import all  modules  in top section:
    from tclCommands import TclCommands.TclCommandExteriors
    at this stage we can include only wanted  commands  with this, auto loading may be implemented in future
    I have no enough knowledge about python's anatomy. Would be nice to include all classes which are descendant etc.

    :param app: FlatCAMApp
    :param commands: List of commands being updated
    :return: None
    """

    tcl_modules = {k: v for k, v in list(sys.modules.items()) if k.startswith('tclCommands.TclCommand')}

    for key, mod in list(tcl_modules.items()):
        if key != 'tclCommands.TclCommand':
            class_name = key.split('.')[1]
            class_type = getattr(mod, class_name)
            command_instance = class_type(app)

            for alias in command_instance.aliases:
                commands[alias] = {
                    'fcn': command_instance.execute_wrapper,
                    'help': command_instance.get_decorated_help()
                }
