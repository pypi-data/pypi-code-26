from abc import ABC, abstractmethod


class HandlerBase(ABC):
    """Base is the abstract base class for Handlers.  A Handler should know 
    how to cache and restore some type of object.
    """

    @abstractmethod
    def understands(self, value):
        """Return a boolean indicating whether this handler knows what to do 
        with the value given.
        """
        pass

    @abstractmethod
    def checksum(self, value):
        """Return a unique identifier string for the value.  Typically, this is a 
        cryptographic hash of the full value.
        """
        pass

    @abstractmethod
    def quicksum(self, value):
        """Return a mostly-unique identifier string for the value that can be 
        used as a quick way to tell if a value has changed.  Typically, this is 
        something like the mtime+size of a file.
        """
        pass

    def checksum_matches_existing(self, value, existing):
        if not existing:
            return False

        qs = self.quicksum(value)
        if qs and qs == existing["quicksum"]:
            return True
        else:
            cs = self.checksum(value)
            return cs == existing["checksum"]

    @abstractmethod
    def serialize(self, value, handle):
        """Serialize the value into a writable IO given by handle.  Additionally,
        You may also return a JSON-serializable Dict, which may contain a 
        **limited** amount of metadata, such as the encoding, etc.
        """
        pass

    @abstractmethod
    def deserialize(self, metadata, handle):
        """Given the metadata (i.e. the return value of the corresponding 
        serialize function) and a readable IO, return the rehydrated object.
        """
        pass
