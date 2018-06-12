from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class Base(object):
    dict_columns = None

    @property
    def columns(self):
        if self.dict_columns != None:
            return [c.name for c in self.__table__.columns if c.name in self.dict_columns]

        return [c.name for c in self.__table__.columns]

    @property
    def columnitems(self):
        return dict([(c, getattr(self, c)) for c in self.columns])

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.columnitems)

    def todict(self):
        return self.columnitems
