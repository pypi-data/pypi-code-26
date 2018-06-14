import creaturecast_project.data.projects as ses
import creaturecast_project.data.project_objects as mod


def get(project=None, asset=None, component=None, version=None):

    if project:
        if asset:
            if component:
                if component is True:
                    return ses.session.query(mod.Component)\
                        .join(mod.Component.asset)\
                        .filter(mod.Asset.name == asset)\
                        .join(mod.Asset.project)\
                        .filter(mod.Project.name == project)\
                        .join().all()
                else:
                    return ses.session.query(mod.Component)\
                        .filter(mod.Component.name == component)\
                        .join(mod.Component.asset)\
                        .filter(mod.Asset.name == asset)\
                        .join(mod.Asset.project)\
                        .filter(mod.Project.name == project)\
                        .join().all()
            else:
                if asset is True:
                    return ses.session.query(mod.Asset)\
                        .join(mod.Asset.project)\
                        .filter(mod.Project.name == project)\
                        .join().all()
                else:
                    return ses.session.query(mod.Asset)\
                        .filter(mod.Asset.name == asset)\
                        .join(mod.Asset.project)\
                        .filter(mod.Project.name == project)\
                        .join().all()
        else:
            if project is True:
                return ses.session.query(mod.Project).all()
            else:
                return ses.session.query(mod.Project).filter(mod.Project.name == project).all()


def create_project(name):
    return mod.Project(name)


def create_asset(name, project):
    return mod.Asset(name=name, project=project)


def create_component(name, asset):
    return mod.Component(name=name, asset=asset)
