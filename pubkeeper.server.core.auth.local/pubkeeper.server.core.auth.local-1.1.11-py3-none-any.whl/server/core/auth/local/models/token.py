from sqlalchemy import Column, Boolean, String
from sqlalchemy.orm import relationship
from .base import Base


class Token(Base):
    __tablename__ = 'tokens'

    token = Column(String, primary_key=True)
    revoked = Column(Boolean, default=False)
    description = Column(String)

    rights = relationship("Right", cascade="all, delete, delete-orphan")
