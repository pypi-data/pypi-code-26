from sqlalchemy.orm import scoped_session, sessionmaker
import json
import sqlalchemy
from sqlalchemy.types import TypeDecorator

session = scoped_session(sessionmaker())

class TextPickleType(TypeDecorator):

    impl = sqlalchemy.Text(256)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value
