import os

from .exceptions import PathError
from .utils import abspath


class FilePath:
    """
    This is a class similar to :py:class:`pathlib.Path`.

    Attributes:
        path_list (:py:class:`list`): The list of elements in the path. This can be modified manually.
        exist_required (:py:class:`bool`): Whether or not this path must exist. This can be modified manually.
        ensure (:py:class:`str`): Whether to create the file or directory automatically. Can be either 'dir', to make it
         a directory, or 'file' to make it a file. It will be created before the :py:attr:`FilePath.exist_required`
         check. This can be modified manually.
        lazy (:py:class:`bool`): Whether or not to run :py:attr:`FilePath.ensure` and :py:attr:`FilePath.exist_required`
         checks when accessing or modifying :py:meth:`FilePath.path`. This can be modified manually.
    """

    def __init__(self, path=".", exist_required=True, ensure=None, lazy=False):
        """
        Args:
             path (``Union[:py:class:`os.PathLike`, :py:class:`str`, :py:class:`bytes`]``): The starting path.
             exist_required: See :py:attr:`FilePath.exist_required`
             ensure: See :py:attr:`FilePath.ensure`
             lazy: See :py:attr:`FilePath.lazy`
        """
        self.path_list = []
        self.exist_required = exist_required
        self.ensure = ensure
        self.path = os.fspath(path)
        self.lazy = lazy

    @property
    def path(self):
        if not self.lazy:
            self.check_exists(self.lazy_path)
        return self.lazy_path

    @path.setter
    def path(self, value):
        value = abspath(value)
        if not self.lazy:
            self.check_exists(value)
        self.path_list = value.split(os.path.sep)

    @property
    def lazy_path(self):
        return os.path.join(*self.path_list)

    def getParent(self, exist_required=None, ensure=None, lazy=None):
        new_file = FilePath(
            self.path,
            (self.exist_required if exist_required is None else exist_required),
            (self.ensure if ensure is None else ensure),
            (self.lazy if lazy is None else lazy),
        )
        new_file.path_list.pop()
        return new_file

    def parent(self):
        self.path_list.pop()
        return self

    def getChild(self, child=None, exist_required=None, ensure=None, lazy=None):
        new_file = FilePath(
            self.path,
            (self.exist_required if exist_required is None else exist_required),
            (self.ensure if ensure is None else ensure),
            (self.lazy if lazy is None else lazy),
        )
        if child:
            new_file.path_list.append(child)
        return new_file

    def child(self, child=None):
        if not child:
            return self
        self.path_list.append(child)
        return self

    def ls(self):
        return os.listdir(self.path)

    def mkdir(self, new=None, exist_ok=False):
        newDir = self.getChild(new)
        if (not exist_ok) and newDir.exists:
            raise PathError("Path %s exists" % newDir.path)
        elif newDir.exists:
            return
        os.makedirs(newDir.path, exist_ok=exist_ok)

    def mkfile(self, new=None, exist_ok=False):
        newDir = self.getChild(new)
        if (not exist_ok) and newDir.exists:
            raise PathError("Path %s exists" % newDir.path)
        elif newDir.exists:
            return
        newDir.open(mode="w").close()

    @property
    def exists(self):
        return os.path.exists(self.path)

    def open(self, file=None, mode="r"):
        return open(self.getChild(file).path, mode)

    @property
    def isdir(self):
        return os.path.isdir(self.path)

    @property
    def isfile(self):
        return os.path.isfile(self.path)

    @property
    def readable(self):
        return os.access(self.path, os.R_OK)

    @property
    def writable(self):
        return os.access(self.path, os.W_OK)

    @property
    def executable(self):
        return os.access(self.path, os.X_OK)

    def unlink(self, file=None):
        os.unlink(self.getChild(file).path)

    def check_exists(self, path):
        if self.ensure.lower().strip().startswith("dir"):
            FilePath(path).mkdir(exist_ok=True)
        elif self.ensure.lower().strip().startswith("file"):
            FilePath(path).mkfile(exist_ok=True)
        if self.exist_required and not os.path.exists(path):
            raise PathError("Path %s does not exist.")

    def __fspath__(self):
        return self.path

    __str__ = __fspath__

    __getitem__ = getChild
