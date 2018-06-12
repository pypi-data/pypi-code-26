from sqlalchemy import (
    Column, Integer, Boolean, String, ForeignKey
)
from .base import Base
from .token import Token


class Right(Base):
    __tablename__ = 'rights'
    dict_columns = ['topic', 'read', 'write']

    id = Column(Integer, primary_key=True)
    token = Column(String, ForeignKey(Token.token))
    topic = Column(String)
    read = Column(Boolean)
    write = Column(Boolean)
