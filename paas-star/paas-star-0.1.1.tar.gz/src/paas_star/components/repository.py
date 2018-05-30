from star_builder import Component
from star_builder.bases import ComponentMeta

from toolkit import _find_caller_name

from .session import Session
from ..logger import get_logger


class RepositoryMeta(ComponentMeta):

    def __new__(mcs, class_name, bases, props):
        """
        创建后更改return annotation
        :param class_name:
        :param bases:
        :param props:
        :return:
        """
        cls = super().__new__(mcs, class_name, bases, props)
        if "resolve" in props:
            props["resolve"].__annotations__['return'] = cls
        return cls


class Repository(Component, metaclass=RepositoryMeta):

    def __init__(self, *args, **kwargs):
        name = kwargs.pop("name", _find_caller_name())
        self.logger = get_logger(name)

    def resolve(self, session: Session):
        """
        每次请求都更新logger.user
        :param session:
        :return:
        """
        self.logger.user = session.user
