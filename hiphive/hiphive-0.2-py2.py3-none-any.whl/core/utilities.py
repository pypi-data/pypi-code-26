"""
The ``utilities`` module contains various support functions and classes.
"""

from ..io.logging import Progress
__all__ = ['Progress']


class BiMap:
    """Simple list like structure with fast dict-lookup

    The structure can append objects and supports some simple list interfaces.
    The lookup is fast since an internal dict stores the indices.
    """
    def __init__(self):
        self._list = list()
        self._dict = dict()

    def __contains__(self, value):
        return value in self._dict

    def __getitem__(self, index):
        return self._list[index]

    def append(self, value):
        """bm.append(hashable) -> None -- append hashable object to end"""
        self._dict[value] = len(self._list)
        self._list.append(value)

    def __len__(self):
        return len(self._list)

    def index(self, value):
        """bm.index(values) -> integer -- return index of value
        Raises ValueError if the values is not present.
        """
        try:
            return self._dict[value]
        except KeyError:
            print(self._dict)
            raise ValueError('{} is not in list'.format(value))

    def copy(self):
        """bm.copy() -> BiMap -- a shallow copy of bm"""
        tbm = BiMap()
        tbm._list = self._list.copy()
        tbm._dict = self._dict.copy()
        return tbm
