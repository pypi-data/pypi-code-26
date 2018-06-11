from pony.orm.core import Database, Entity, EntityMeta
from pony.utils import cut_traceback


db = Database()


class _EntityMeta(EntityMeta):
    def __new__(meta, name, bases, cls_dict):
        if hasattr(db, name):
            return getattr(db, name)
        return super(_EntityMeta, meta).__new__(meta, name, bases, cls_dict)

    @cut_traceback
    def __init__(entity, name, bases, cls_dict):
        if hasattr(db, name):
            entity = getattr(db, name)
        else:
            super(_EntityMeta, entity).__init__(name, bases, cls_dict)


Entity = type.__new__(_EntityMeta, 'Entity', (Entity,), {})
Entity._database_ = db
