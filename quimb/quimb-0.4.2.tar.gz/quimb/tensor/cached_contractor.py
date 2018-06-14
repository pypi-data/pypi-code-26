import functools
import numpy as np


transpose = np.transpose
einsum = np.einsum


@functools.lru_cache(1)
def get_hasher():
    """
    """
    import xxhash

    return xxhash.xxh64()


def hashxx(obj):
    """
    """
    # return id(obj)
    h = get_hasher()
    h.update(np.require(obj, requirements=['C']))
    hsh = h.intdigest()
    h.reset()
    return hsh


@functools.lru_cache(1)
def get_cache(size):
    """
    """
    import lru

    return lru.LRU(size)


_CONTRACT_CACHE_SIZE = 1024


def get_contract_cache_size():
    global _CONTRACT_CACHE_SIZE
    return _CONTRACT_CACHE_SIZE


def set_contract_cache_size(size):
    global _CONTRACT_CACHE_SIZE
    _CONTRACT_CACHE_SIZE = size


def clear_contract_cache():
    """
    """
    cache = get_cache(_CONTRACT_CACHE_SIZE)
    cache.clear()


HITCOUNT = 0
MISSCOUNT = 0


def tensordot(x, y, axes=2):
    """
    """
    global HITCOUNT, MISSCOUNT

    key = (hashxx(x), hashxx(y), hash(axes))
    cache = get_cache(_CONTRACT_CACHE_SIZE)

    if key not in cache:
        z = np.tensordot(x, y, axes=axes)
        cache[key] = z
        MISSCOUNT += 1
        return z

    HITCOUNT += 1

    return cache[key]
