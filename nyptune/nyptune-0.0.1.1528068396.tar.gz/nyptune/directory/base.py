from abc import ABC, abstractmethod


class DirectoryBase(ABC):
    """Base is the abstract base class for Directories.  A Directory exposes a
    subset of expected Posix functionality, in order to make it easier to implement.
    For example, you might have an S3-backed directory.
    """

    @abstractmethod
    def glob(self, pattern):
        """Return a list of matching files
        """
        pass

    @abstractmethod
    def remove(self, name):
        """Delete a file
        """
        pass

    @abstractmethod
    def exists(self, name):
        """Return a boolean if the file with this name exists
        """
        pass

    @abstractmethod
    def writer(self, name):
        """Return an write-mode IO for the file name.
        """
        pass

    @abstractmethod
    def reader(self, name):
        """Return an read-mode IO for the file name.
        """
        pass
