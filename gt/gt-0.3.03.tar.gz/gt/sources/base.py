from abc import ABC, abstractmethod

class GitSource(ABC):
    @abstractmethod
    def location(self, name):
        """Returns a URL corresponding to the location of repository {name}. Must
           be git clonable. Does not perform validation (confirm existence)"""
        pass

    @abstractmethod
    def create(self, name, is_private=True):
        """Creates a new repository called {name} within the given source."""
        pass

    @abstractmethod
    def list(self):
        """Returns all repositories contained within the provided source."""
        pass

    @abstractmethod
    def delete(self, name):
        """Deletes the named repository within the given sourc."""
        pass