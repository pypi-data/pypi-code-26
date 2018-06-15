import os
import json
import sqlalchemy
from os.path import expanduser
from sqlalchemy.orm import scoped_session, sessionmaker
import creaturecast_project.data.project_objects as pob
import creaturecast_environment.settings as set
home_directory = expanduser("~").replace('\\', '/')
local_user = os.getenv('USER')
creaturecast_directory = '%s/creaturecast' % home_directory

set.add_settings(
    dict(
        name='projects_directory',
        value='',
        widget_class='creaturecast_settings_manager.widgets.settings_manager.SettingsPath'
        ),
    dict(
        name='projects_database',
        value='%s/projects/projects.db' % creaturecast_directory,
        widget_class='creaturecast_settings_manager.widgets.settings_manager.SettingsPath'
        )
    )

projects_database_path = set.get_setting('projects_database').value
projects_database_directory = os.path.dirname(projects_database_path)

if not os.path.exists(projects_database_directory):
    os.makedirs(projects_database_directory)


'''This should be removed for final product'''
#if os.path.exists(projects_database_path):
#    os.remove(projects_database_path)

engine = sqlalchemy.create_engine("sqlite:///%s" % projects_database_path)
engine.echo = False
pob.Base.metadata.bind = engine
pob.Base.metadata.create_all()
session = scoped_session(sessionmaker())
session.configure(bind=engine)

'''
if not session.query(pob.Project).all():

    for x in range(1):
        with open('%s/movies.json' % os.path.dirname(pob.__file__.replace('\\', '/')), mode='r') as f:

            for movie_data in json.loads(f.read()):
                project = pob.Project(
                    name=movie_data['title'],
                    icon='/images/icons/folder_closed.png'
                )
                for i in range(40):
                    asset = pob.Asset(
                        name='Digidouble_%s' % i,
                        project=project,
                        icon='/images/icons/default_user.png'
                    )
                    for component_name in ['geometry', 'tissue_geometry', 'body_rig', 'face_rig', 'texture']:
                        component = pob.Component(
                            name='%s' % component_name,
                            asset=asset,
                            icon='/images/icons/polygon.png'
                        )
                        for version_number in range(10):
                            component_version = pob.ComponentVersion(
                                component=component,
                                icon='/images/icons/polygon.png'
                            )
                session.add(project)
                session.commit()
'''