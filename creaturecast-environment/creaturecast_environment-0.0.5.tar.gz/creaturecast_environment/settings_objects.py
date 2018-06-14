import json
from sqlalchemy.types import TypeDecorator
from sqlalchemy import Column, Integer, String, Text, MetaData
from sqlalchemy.ext.declarative import declarative_base


metadata = MetaData()
Base = declarative_base(metadata)

class TextPickleType(TypeDecorator):

    impl = Text(256)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class Setting(Base):

    __tablename__ = 'setting'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    widget_class = Column(String(100), nullable=True)
    value = Column(TextPickleType())

    def __init__(self, **kwargs):

        self.name = kwargs['name']
        self.value = kwargs['value']
        self.widget_class = kwargs.get('widget_class', None)

    def __repr__(self):
        return "Setting(id=%s, name=%s)" % (
                    self.id,
                    self.name
                )
