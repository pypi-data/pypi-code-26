import sys
from collections import OrderedDict
from nulltype import NullType

__all__ = 'Empty Item itemize itemize_all'.split()

_PY2 = sys.version_info[0] == 2
if not _PY2:
    basestring = str

Empty = NullType('Empty')

SIMPLE_TYPES = (int, float, complex, basestring, bytes)

def _item(data):
    """
    Private factory function for Item values, especially second and subsequent
    levels beneath the top-level mapping. Here because recursive initializers
    in Python aren't straightforward (and maybe not really even feasible, 
    since some recursions would not yield Item results, but lists or other
    data types).
    """
    if isinstance(data, SIMPLE_TYPES):
        return data
    if hasattr(data, 'items'):
        it = Item()
        for k, v in data.items():
            it[k] = _item(v)
        return it
    if isinstance(data, (list, tuple)):
        return type(data)(_item(x) for x in data)
    return data


class Item(OrderedDict):
    
    def __init__(self, a_dict=None, **kwargs):
        super(Item, self).__init__()
        if a_dict:
            for k, v in a_dict.items():
                super(Item, self).__setitem__(k, _item(v))
        if kwargs:
            self.update(_item(kwargs))

    def __getattr__(self, name):
        try:
            return super(Item, self).__getitem__(name)
        except KeyError:
            return Empty
        
    def __getitem__(self, key):
        try:
            return super(Item, self).__getitem__(key)
        except (IndexError, KeyError):
            return Empty
        
    def __repr__(self):
        clsname = self.__class__.__name__
        kwstr = ', '.join('{0}={1!r}'.format(k, v) for k, v in self.items())
        return '{0}({1})'.format(clsname, kwstr)
    
    @classmethod
    def from_tuples(cls, data):
        it = cls()
        for tup in data:
            k, v = tup
            it[k] = _item(v)
        return it

def itemize(iterator):
    """
    Given a collection of dict-like records, create and 
    return an Item out of each record.
    """
    for item in iterator:
        yield Item(item)


def itemize_all(iterator):
    """
    Given a collection of dict-like records, create and 
    return an list of Item objects comprising all the records.
    """
    return list(itemize(iterator))