import os

from . import FilePath


class Path:
    """
    This is a class for working with PATHs, like PATH or MANPATH.

    It has the interface of a list. It loads the initial list from an environment variable,
    and converts each element into a :class:`~ostools.FilePath`, with ``exist_required`` set to false.

    Attributes:
        envvar (:py:class:`str`): The environment variable to load the paths from.
        items (:py:class:`list`): The list of paths.
    """

    def __init__(self, envvar="PATH"):
        """
        Args:
            envvar (str): The environment variable to load the paths from.
        """
        self.envvar = envvar
        self.items = []
        self.reload()

    def reload(self):
        """
        Load the PATH from the environment variable specified in :attr:`envvar`, converting each element into a
        :class:`~ostools.FilePath`, with ``exist_required`` set to false.
        """
        items = os.environ.get(self.envvar, "").split(":")
        for item in items:
            self.items.append(FilePath(item, exist_required=False))

    def __iter__(self):
        return iter(self.items)

    def __contains__(self, item):
        return item in self.items

    def __len__(self):
        return len(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __setitem__(self, key, value):
        self.items[key] = FilePath(value, exist_required=False)

    def __getattr__(self, item):
        return getattr(self.items, item)

    def append(self, item):
        """
        This function functions like :py:meth:`list.append`. It also converts the ``item`` into a
        :class:`~ostools.FilePath`, with ``exist_required`` set to false.
        """
        self.items.append(FilePath(item, exist_required=False))

    def extend(self, items):
        """
        This function functions like :py:meth:`list.extend`.
        It also converts each item into a
        :class:`~ostools.FilePath`, with ``exist_required`` set to false.
        """
        for item in items:
            self.append(item)

    def insert(self, index, item):
        """
        This function functions like :py:meth:`list.insert`. It also converts the ``item`` into a
        :class:`~ostools.FilePath`, with ``exist_required`` set to false.
        """
        self.items.insert(index, FilePath(item, exist_required=False))
