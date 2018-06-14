import os
from os.path import expanduser
import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker
import creaturecast_environment.settings_objects as sob

package_name = __file__.replace('\\', '/').split('/')[-2]
home_directory = expanduser("~").replace('\\', '/')
local_user = os.getenv('USER')
creaturecast_directory = '%s/creaturecast' % home_directory
environment_database_path = '%s/environment.db' % creaturecast_directory


if not os.path.exists(creaturecast_directory):
    os.makedirs(creaturecast_directory)

engine = sqlalchemy.create_engine("sqlite:///%s" % environment_database_path)
engine.echo = False
sob.Base.metadata.bind = engine
sob.Base.metadata.create_all()
session = scoped_session(sessionmaker())
session.configure(bind=engine)


def get_setting(name):
    return session.query(sob.Setting).filter(sob.Setting.name == name).first()


def add_settings(*args):
    existing_settings = dict((x.name, x) for x in session.query(sob.Setting).all())
    for x in args:
        if x['name'] not in existing_settings:
            new_setting = sob.Setting(**x)
            session.add(new_setting)
    session.commit()


class Settings(object):
    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__()

    def __getitem__(self, name):
        setting = session.query(sob.Setting).filter(sob.Setting.name == name).first()
        if setting:
            return setting.value

    def __setitem__(self, name, value):
        new_setting = sob.Setting(name=name, value=value)
        session.add(new_setting)
        session.commit()
        return new_setting


settings = Settings()