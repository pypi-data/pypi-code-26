class _slices:
    """用多个 slice 切分序列

    >>> slices[:4, 4:6, 6:]('20180612')
    ('2018', '06', '12')
    """
    _slices = None

    def __getitem__(self, slices):
        self._slices = slices
        return self

    def __call__(self, obj):
        return tuple(obj[s] for s in self._slices)


slices = _slices()


class cut:
    """用多个整数切分序列

    >>> cut(4, 6)('20180612')
    ('2018', '06', '12')
    """

    def __init__(self, *indices):
        self._indices = indices

    def __call__(self, obj):
        starts = (None,) + self._indices
        ends = self._indices + (None,)
        return tuple(obj[start:stop] for start, stop in zip(starts, ends))
