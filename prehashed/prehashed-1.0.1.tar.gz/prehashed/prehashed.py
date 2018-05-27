from hashlib import sha1
from itertools import chain

def sha1_fn(i):
    """Hash the string representation with sha1.

    Args:
        hashable: An object to hash.

    Returns:
        int: The hash.
    """
    return int(sha1(str(i).encode('utf-8')).hexdigest(), 16)

class PrehashedDict(dict):
    """A dictionary where the keys are hashed before they are added.

    Args:
        mapping: Initial data to add to the dict. Default: ``()``
        hash_fn: The function used to hash keys. Default: ``sha1_fn``
    """
    __slots__ = ('_hash')

     # Creating
    def __init__(self, mapping=(), hash_fn=sha1_fn, **kwargs):
        self._hash = hash_fn
        super().__init__(self._process_args(mapping, **kwargs))

    def _process_args(self, mapping=(), **kwargs):
        if isinstance(mapping, PrehashedDict):
            d = [(k, v) for k, v in mapping.items()]
            d.extend([(self._hash(k), v) for k, v in kwargs.items()])
            return d
        if hasattr(mapping, 'items'):
            mapping = mapping.items()
        return ((self._hash(k), v) for k, v in chain(mapping, kwargs.items()))

    def update(self, mapping=(), **kwargs):
        super().update(self._process_args(mapping, **kwargs))

    @classmethod
    def fromkeys(self, keys, v=None):
        return super().fromkeys(keys, v)

    def copy(self):
        return type(self)(self)

    # Setting
    def __setitem__(self, k, v):
        super().__setitem__(self._hash(k), v)

    def setdefault(self, k, default=None):
        return super().setdefault(self._hash(k), default)

    def initial_add(self, k, v):
        """Keep adding a zero width space until it can be inserted."""
        zero_width_space = '\u200B'
        k = str(k)
        while super().__contains__(self._hash(k)):
            k = k + zero_width_space
        self.__setitem__(k, v)
        return k

    # Getting
    def __getitem__(self, k):
        return super().__getitem__(self._hash(k))

    def get(self, k, default=None):
        return super().get(k, default)

    def pop(self, k, v=None):
        if v is None:
            return super().pop(self._hash(k))
        return super().pop(self._hash(k), v)

    # Removing
    def __delitem__(self, k):
        return super().__delitem__(self._hash(k))

    # Checking
    def __contains__(self, k):
        return super().__contains__(self._hash(k))

    # Saving
    def __getstate__(self):
        return [self._hash, dict(self)]

    def __setstate__(self, state):
        h, data = state
        self._hash = h
        # Call supers update to avoid double hashing
        super().update(data)

    def __reduce__(self):
        return (PrehashedDict, (), self.__getstate__())
