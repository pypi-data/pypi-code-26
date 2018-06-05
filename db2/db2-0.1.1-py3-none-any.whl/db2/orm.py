#! usr/bin/python3.6

import backend
from collections import ChainMap

class BaseMeta(type):
    @classmethod
    def __prepare__(cls, name, bases):
        fields_dict = {key:val for key, val in backend.__dict__.items()
        if isinstance(val, backend.DescriptorMeta)}

        return dict(ChainMap({}, fields_dict))

    def __call__(self, *args, **kwargs):
        clsobj = type.__call__(self, *args)

        for name, value in kwargs.items():
            if name in self._fields:
                setattr(clsobj, name, value)
            else:
                raise TypeError('%s is not defined in class %s'%(name, self.__name__))

        return clsobj


class Base(metaclass=BaseMeta):
    subclasses = {}

    def __init_subclass__(cls):
        def columns(cls):
            d = {k:v for k, v in cls.__dict__.items() 
            if isinstance(v, backend.Descriptor)}
            assert 'id' in vars(cls), "Specify 'id' field as primary_key'" +\
            " e.g: id = PositiveInteger(primary_key=True) in class %s"%cls.__name__
            
            return d

        types = {key:val for key, val in vars(cls).items()
                  if isinstance(val, backend.Descriptor)}
        fields =[key for key in types]

        for name in fields:
            vars(cls)[name].name = name

        setattr(cls, '_fields', fields)
        setattr(cls, 'types', types)
        setattr(cls, 'columns', columns(cls))
        Base.subclasses[cls.__name__] = cls


    def __repr__(self):
        params = ', '.join("%s='%s'" % (key, val)
                for key, val in vars(self).items() 
                if not key.startswith("_"))

        return f'{type(self).__name__}({params})'



__all__ = ['Base']

