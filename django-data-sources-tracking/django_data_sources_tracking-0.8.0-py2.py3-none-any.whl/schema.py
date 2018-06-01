from graphene import Node, String
from graphene_django import DjangoObjectType

from . import choices, models


class FileNode(DjangoObjectType):

    type = String()

    class Meta:
        model = models.File
        interfaces = (Node, )

    def resolve_type(self, info):
        return choices.FILE_TYPES[self.type]
