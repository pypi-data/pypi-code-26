"""Utils."""
import logging

logger = logging.getLogger(__name__)


class DotMap(dict):
    """DotMap from a dictionary.

    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        """."""
        super().__init__(*args, **kwargs)

        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super().__delitem__(key)
        del self.__dict__[key]

    def as_json(self):
        """Return json/dict of key-value pairs."""
        return self.__dict__


class DotMapJob(DotMap):
    """DotMap Job which contains DotMap tasks."""

    def __init__(self, *args, **kwargs):
        """."""
        super().__init__(*args, **kwargs)

        if len(self.tasks) != 0:
            self.tasks = [DotMap(task_dict) for task_dict in self.tasks]


class DotMapTask(DotMap):
    """DotMap Task which is just an alias for DotMap."""
    pass
