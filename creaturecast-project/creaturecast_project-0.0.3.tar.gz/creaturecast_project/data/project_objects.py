import datetime
import os
import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
import creaturecast_project.data.data_types as dtp
import creaturecast_environment
import creaturecast_environment.settings as stt


metadata = MetaData()
Base = declarative_base(metadata)


class Project(Base):

    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    data = Column(dtp.TextPickleType())
    created = Column(DateTime, default=datetime.datetime.now())
    changed = Column(DateTime, default=datetime.datetime.now())
    uuid = Column(String(100), nullable=False)

    assets = relationship(
        'Asset',
        backref=backref("project", remote_side='Project.id'),

    )

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__()
        if not kwargs and args and isinstance(args[0], dict):
            kwargs = args[0]
        self.name = kwargs.get('name', None)
        self.data = kwargs
        self.uuid = str(uuid.uuid4())

        #os.makedirs(self.get_path())

    def iterate_children(self):
        for asset in self.assets:
            yield asset


    def __repr__(self):
        return "Project(id=%s, name=%s)" % (
                    self.id,
                    self.name
                )


    def get_owner(self):
        return None

    def get_path(self):
        projects_directory = stt.get_setting('projects_directory').value
        if not projects_directory:
            database_path = stt.get_setting('projects_database').value
            projects_directory = os.path.dirname(database_path)
        return '%s/%s' % (projects_directory, self.name)

    def serialize(self):
        data = self.data
        data.update(id=self.id)

        #data['created'] = self.created
        #data['changed'] = self.changed
        return data

class Asset(Base):

    __tablename__ = 'asset'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('asset.id'))
    name = Column(String(100), nullable=False)
    data = Column(dtp.TextPickleType())
    created = Column(DateTime, default=datetime.datetime.now())
    changed = Column(DateTime, default=datetime.datetime.now())
    uuid = Column(String(100), nullable=False)

    children = relationship('Asset',

                        # cascade deletions
                        cascade="all",

                        # many to one + adjacency list - remote_side
                        # is required to reference the 'remote'
                        # column in the join condition.
                        backref=backref("parent", remote_side='Asset.id'),

                        # children will be represented as a dictionary
                        # on the "name" attribute.
                        #collection_class=collections.attribute_mapped_collection('name'),
                    )

    project_id = Column(Integer, ForeignKey('project.id'))

    components = relationship(
        'Component',
        backref=backref("asset", remote_side='Asset.id'),

    )

    rigs = relationship(
        'Rig',
        backref=backref("asset", remote_side='Asset.id'),

    )

    def iterate_children(self):
        for component in self.components:
            yield component

        for rig in self.rigs:
            yield rig


    def __init__(self, *args, **kwargs):
        super(Asset, self).__init__()
        if not kwargs and args and isinstance(args[0], dict):
            kwargs = args[0]
        self.project = kwargs.pop('project')
        self.project.assets.append(self)
        self.name = kwargs.get('name')
        self.data = kwargs
        self.uuid = str(uuid.uuid4())

    def __repr__(self):
        return "Asset(id=%s, name=%s)" % (
                    self.id,
                    self.name
                )

    def get_owner(self):
        return self.project

    def get_path(self):
        return '%s/%s' % (self.get_owner().get_path(), self.name)


    def serialize(self):
        data = self.data
        data.update(id=self.id)

        #data['created'] = self.created
        #data['changed'] = self.changed
        return data

class Component(Base):

    __tablename__ = 'component'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('component.id'))
    data = Column(dtp.TextPickleType())
    name = Column(String(100), nullable=False)
    extension = Column(String(100))
    component_type = Column(String(100))
    uuid = Column(String(100), nullable=False)

    versions = relationship(
        'ComponentVersion',
        backref=backref("component", remote_side='Component.id'),
    )
    asset_id = Column(Integer, ForeignKey('asset.id'))
    created = Column(DateTime, default=datetime.datetime.now())
    changed = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, *args, **kwargs):
        if not kwargs and args and isinstance(args[0], dict):
            kwargs = args[0]
        self.asset = kwargs.pop('asset')
        self.asset.components.append(self)
        self.name = kwargs.get('name', None)
        self.extension = kwargs.get('extension', 'abc')
        self.component_type = kwargs.get('type', self.extension)

        self.data = kwargs
        self.data['extension'] = self.extension
        self.uuid = str(uuid.uuid4())


    def iterate_children(self):
        for versions in self.versions:
            yield versions

    def __repr__(self):
        return "Component(id=%r, name=%r)" % (
                    self.id,
                    str(self.name)
                )

    def get_owner(self):
        return self.asset

    def get_path(self):
        latest_version = self.get_latest_version()
        if latest_version:
            return latest_version.get_path()

    def get_latest_version(self):
        if self.versions:
            return self.versions[-1]


    def serialize(self):
        data = self.data
        data.update(id=self.id)

        #data['created'] = self.created
        #data['changed'] = self.changed
        return data



class Rig(Base):

    __tablename__ = 'rig'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('rig.id'))
    data = Column(dtp.TextPickleType())
    name = Column(String(100), nullable=False)
    extension = Column(String(100))
    uuid = Column(String(100), nullable=False)

    versions = relationship(
        'RigVersion',
        backref=backref("rig", remote_side='Rig.id'),
    )

    asset_id = Column(Integer, ForeignKey('asset.id'))
    created = Column(DateTime, default=datetime.datetime.now())
    changed = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, *args, **kwargs):
        if not kwargs and args and isinstance(args[0], dict):
            kwargs = args[0]
        self.asset = kwargs.pop('asset')
        self.asset.rigs.append(self)
        self.name = kwargs.get('name', None)
        self.extension = 'json'
        self.data = kwargs
        self.uuid = str(uuid.uuid4())

    def iterate_children(self):
        for versions in self.versions:
            yield versions

    def __repr__(self):
        return "Rig(id=%r, name=%r)" % (
                    self.id,
                    str(self.name)
                )

    def get_owner(self):
        return self.asset

    def get_path(self):
        latest_version = self.get_latest_version()
        if latest_version:
            return latest_version.get_path()

    def get_latest_version(self):
        if self.versions:
            return self.versions[-1]


    def serialize(self):
        data = self.data
        data.update(id=self.id)

        #data['created'] = self.created
        #data['changed'] = self.changed
        return data


class ComponentVersion(Base):

    __tablename__ = 'component_version'

    id = Column(Integer, primary_key=True)
    version = Column(Integer)
    component_id = Column(Integer, ForeignKey('component.id'))

    data = Column(dtp.TextPickleType())
    name = Column(String(100), nullable=False)
    created = Column(DateTime, default=datetime.datetime.now())
    changed = Column(DateTime, default=datetime.datetime.now())
    uuid = Column(String(100), nullable=False)

    def __init__(self, *args, **kwargs):
        if not kwargs and args and isinstance(args[0], dict):
            kwargs = args[0]
        self.component = kwargs.pop('component')
        self.component.versions.append(self)
        version = kwargs.get('version', None)
        if version is None:
            version = len(self.component.versions)-1
        self.version = version
        self.data = kwargs
        self.name = '%s_v%s' % (self.component.name, self.version)
        self.data['name'] = self.name
        self.uuid = str(uuid.uuid4())


    def __repr__(self):
        return "ComponentVersion(id=%r, name=%r)" % (
                    self.id,
                    str(self.name)
                )

    def get_owner(self):
        return self.component

    def get_path(self):
        return '%s/%s_v%s.%s' % (self.get_owner().get_owner().get_path(),
                                 self.get_owner().name,
                                 self.version,
                                 self.get_owner().extension
                                 )




class RigVersion(Base):

    __tablename__ = 'rig_version'

    id = Column(Integer, primary_key=True)
    version = Column(Integer)
    rig_id = Column(Integer, ForeignKey('rig.id'))

    data = Column(dtp.TextPickleType())
    name = Column(String(100), nullable=True)
    created = Column(DateTime, default=datetime.datetime.now())
    changed = Column(DateTime, default=datetime.datetime.now())
    uuid = Column(String(100), nullable=True)

    def __init__(self, *args, **kwargs):
        if not kwargs and args and isinstance(args[0], dict):
            kwargs = args[0]

        self.rig = kwargs.pop('rig')
        if 'icon' not in kwargs:
            kwargs['icon'] = self.rig.data['icon']
        self.rig.versions.append(self)
        version = kwargs.get('version', None)
        if version is None:
            version = len(self.rig.versions)-1
        self.version = version
        self.data = kwargs
        self.name = '%s_v%s' % (self.rig.name, self.version)
        self.data['name'] = self.name
        self.uuid = str(uuid.uuid4())
        print self.__dict__

    def __repr__(self):
        return "RigVersion(id=%r, name=%r)" % (
                    self.id,
                    str(self.name)
                )

    def get_owner(self):
        return self.rig

    def get_path(self):
        return '%s/%s_v%s.%s' % (self.get_owner().get_owner().get_path(),
                                 self.get_owner().name,
                                 self.version,
                                 self.get_owner().extension
                                 )
