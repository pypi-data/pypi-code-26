from typing import List
def deduplicateList(anyList: List, preserveOrder = False):
    """
    Deduplicates a list.
    
    Does not preserve order by default, because it is faster.
    
    Parameters
    ----------
    anyList : list
        The list to be deduplicated.
    preserveOrder : bool, optional
        If *True*, preserves order of elements in the list.
    
    Returns
    -------
    List
        A new list, containing all elements of `anyList`, but only once. 
    """
    if preserveOrder == False:
        return _deduplicateListNonPreserving(anyList)
    else:
        return _deduplicateListPreserving(anyList)
    

def _deduplicateListNonPreserving(anyList: List):
    keys = {}
    for e in anyList:
        keys[e] = 1
    return list( keys.keys() )


def _deduplicateListPreserving(seq: List, idfun=None):
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result


def chunks(iterable, chunk_size):
    """
    Chops Iterable into chunks.
    
    Parameters
    ----------
    iterable : Iterable
        The Iterable object to be chunked.
    chunk_size : int
        The size if each chunk. Except for the last, of course.
    
    Yields
    -------
    Iterable
        Iterable of the same type as `iterable`, but with length `chunk_size`. Except for the last, of course.
    """
    for i in range(0, len(iterable), chunk_size):
        yield iterable[i:i + chunk_size]
