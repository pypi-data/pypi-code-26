from hashlib import sha1
from itertools import chain

def sha1_fn(i):
    return int(sha1(str(i).encode('utf-8')).hexdigest(), 16)

class PrehashedDict(dict):
    r"""A dictionary where the keys are hashed before they are added.

    Note:
        This hashes keys with sha1 before hand (user can provide a different
        hash if they want). The chance of a collision is 1 in 2^64. Ignoring
        this chance is how git compares files.

    Note:
        The point of this is that we can store keys that are really large (long
        strings) cheaply. For example when storing the documents in the
        tokenized Dailymail dataset (https://drive.google.com/file/d/0BzQ6rtO2VN95bndCZDdpdXJDV1U/view)
        the keys take up 1.018 GB while this implementation takes 10.53 MB.

    Note:
        A small space saving (7.79 MB vs 10.53 MB) can be found using the built in
        `hash` function the results of this are not shareable across runs.

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
        """Keep adding a zero width space utill it can be inserted."""
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
