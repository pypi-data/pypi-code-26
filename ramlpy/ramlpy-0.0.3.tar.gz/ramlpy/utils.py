import re


_underscorer1 = re.compile(r'(.)([A-Z][a-z]+)')
_underscorer2 = re.compile('([a-z0-9])([A-Z])')


def snake_case(s: str) -> str:
    subbed = _underscorer1.sub(r'\1_\2', s)
    return _underscorer2.sub(r'\1_\2', subbed).lower()


def topological_sort(source):
    """perform topo sort on elements.

    :arg source: list of ``(name, [list of dependancies])`` pairs
    :returns: list of names, with dependancies listed first
    """
    # copy deps so we can modify set in-place
    pending = [(name, set(deps)) for name, deps in source]
    emitted = []
    while pending:
        next_pending = []
        next_emitted = []
        for entry in pending:
            name, deps = entry
            deps.difference_update(emitted)  # remove deps we emitted last pass
            if deps:  # still has deps? recheck during next pass
                next_pending.append(entry)
            else:  # no more deps? time to emit
                yield name
                emitted.append(name)  # <-- not required, but helps preserve original ordering
                next_emitted.append(name)  # remember what we emitted for difference_update() in next pass
        if not next_emitted:  # all entries have unmet deps, one of two things is wrong...
            raise ValueError("cyclic or missing dependancy detected: %r" % (next_pending, ))
        pending = next_pending
        emitted = next_emitted