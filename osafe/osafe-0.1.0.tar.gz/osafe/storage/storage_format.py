from abc import ABC, abstractproperty, abstractmethod


class StorageFormat(ABC):
    FILENAME = "osafe.json"

    @abstractproperty
    def exists(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self, content):
        pass

    @abstractmethod
    def clear(self):
        pass
