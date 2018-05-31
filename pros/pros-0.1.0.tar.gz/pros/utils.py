
class cached_property(object):  # noQA
    """
    A property that is only computed once per instance and then replaces
    itself with an ordinary attribute. Deleting the attribute resets the
    property.

    https://github.com/bottlepy/bottle/blob/fa7733e075da0d790d809aa3d2f53071897e6f76/bottle.py#L147
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = self.func(obj)
        obj.__dict__[self.func.__name__] = value
        return value
