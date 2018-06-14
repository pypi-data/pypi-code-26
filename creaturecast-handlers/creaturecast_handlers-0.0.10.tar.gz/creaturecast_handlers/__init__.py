__version__ = '0.0.10'
__description__ = 'Creaturecast Handlers'
__author__ = 'Paxton Gerrish'
__email__ = 'creaturecastlabs@gmail.com'
__url__ = 'https://github.com/Paxtongerrish/creaturecast_handlers.git'


import PySignal
import time
import creaturecast_project.data.project_objects as pob
import creaturecast_project.data.projects as pjs


class NodeHandler(object):

    created = PySignal.ClassSignal()
    start_parent = PySignal.ClassSignal()
    end_parent = PySignal.ClassSignal()
    start_unparent = PySignal.ClassSignal()
    end_unparent = PySignal.ClassSignal()
    end_create = PySignal.ClassSignal()
    deleted = PySignal.ClassSignal()

    def __init__(self, *args, **kwargs):
        super(NodeHandler, self).__init__()


class SelectionHandler(object):

    selection_changed = PySignal.ClassSignal()

    def __init__(self, *args, **kwargs):
        super(SelectionHandler, self).__init__()
        self.selected_nodes = set()

    def select_nodes(self, *nodes):
        self.selected_nodes = nodes
        self.selection_changed.emit(self.selected_nodes)


class UserHandler(object):

    user_changed = PySignal.ClassSignal()

    def __init__(self, *args, **kwargs):
        super(UserHandler, self).__init__()
        self.current_user = None

    def set_user(self, user):
        self.current_user = user
        self.user_changed.emit(user)


class RigHandler(object):

    rig_changed = PySignal.ClassSignal()
    load_rig = PySignal.ClassSignal()

    def __init__(self, *args, **kwargs):
        super(RigHandler, self).__init__()
        self.current_rig = None

    def set_rig(self, user):
        self.current_rig = user
        self.rig_changed.emit(user)


class ErrorHandler(object):

    error = PySignal.ClassSignal()

    def __init__(self, *args, **kwargs):
        super(ErrorHandler, self).__init__()


class ProjectHandler(object):

    project_changed = PySignal.ClassSignal()
    project_created = PySignal.ClassSignal()
    project_deleted = PySignal.ClassSignal()
    asset_changed = PySignal.ClassSignal()
    asset_created = PySignal.ClassSignal()
    asset_deleted = PySignal.ClassSignal()
    component_changed = PySignal.ClassSignal()
    component_created = PySignal.ClassSignal()
    component_deleted = PySignal.ClassSignal()
    component_version_changed = PySignal.ClassSignal()
    component_version_created = PySignal.ClassSignal()
    component_version_deleted = PySignal.ClassSignal()

    def __init__(self, *args, **kwargs):
        super(ProjectHandler, self).__init__()
        self.current_project = None
        self.current_asset = None
        self.current_component = None
        self.current_component_version = None

    def set_project(self, project):
        self.current_project = project
        self.project_changed.emit(project)

    def delete_project(self, project):
        self.project_deleted.emit(project)
        pjs.session.delete(project)
        pjs.session.commit()

    def set_asset(self, asset):
        self.current_asset = asset
        self.asset_changed.emit(asset)

    def create_asset(self, data):
        new_asset = pob.Asset(**data)
        pjs.session.add(new_asset)
        pjs.session.commit()
        self.asset_created.emit(new_asset)
        self.set_asset(new_asset)

    def delete_asset(self, asset):
        self.asset_deleted.emit(asset)
        pjs.session.delete(asset)
        pjs.session.commit()

    def set_component(self, component):
        self.current_component = component
        self.component_changed.emit(component)

    def delete_component(self, component):
        self.component_deleted.emit(component)
        pjs.session.delete(component)
        pjs.session.commit()

    def set_component_version(self, component_version):
        self.current_component_version = component_version
        self.component_version_changed.emit(component_version)

    def delete_component_version(self, component_version):
        self.component_version_deleted.emit(component_version)
        pjs.session.delete(component_version)
        pjs.session.commit()


user_handler = UserHandler()
selection_handler = SelectionHandler()
node_handler = NodeHandler()
error_handler = ErrorHandler()
project_handler = ProjectHandler()
