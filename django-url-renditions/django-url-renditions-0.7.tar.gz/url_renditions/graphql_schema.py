import graphene
from graphene_django import DjangoObjectType
from . import models
from django.db.models.fields.reverse_related import OneToOneRel


class Rendition(DjangoObjectType):
    class Meta:
        model = models.Rendition
        filter_fields = ['id', 'name']
        interfaces = (graphene.relay.Node, )


def call_that_returns_fields_dict():
    result = {}
    for name in ['small', 'medium']:
        result[name] = graphene.Field(Rendition)
    return result


def get_fields_dict():
    rendition_names = []
    for field in models.Original._meta.get_fields():
        if type(field) is OneToOneRel:
            rendition_names += field.field.renditions.keys()
    result = {}
    for name in set(rendition_names):
        result[name] = graphene.Field(Rendition)
    return result


Renditions = type('Renditions', (graphene.ObjectType,), get_fields_dict())


class Original(DjangoObjectType):

    renditions = graphene.Field(Renditions)

    class Meta:
        model = models.Original
        filter_fields = ['id']
        interfaces = (graphene.relay.Node, )

    def resolve_renditions(self, info, **kwargs):
        renditions = {}
        for r in self.rendition_set.all():
            renditions[r.name] = r
        return Renditions(**renditions)


class Query(object):
    original = graphene.relay.Node.Field(Original)
    rendition = graphene.relay.Node.Field(Rendition)
