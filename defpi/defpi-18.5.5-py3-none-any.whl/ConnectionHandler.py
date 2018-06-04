from abc import abstractmethod

__all__ = ['ConnectionHandler', 'InterfaceInfo']


class InterfaceInfo:
    def __init__(self, name: str, version: str, receivesHash: str, sendsHash: str, serializer: str):
        self.name = name
        self.version = version
        self.receivesHash = receivesHash
        self.sendsHash = sendsHash
        self.serializer = serializer


class ConnectionHandler:
    """The ConnectionHandler provides the functionality to deal with changing connection statuses.

    Specific functions that deal with incoming messages will be called when the messages are received through the
    connection. Reflection is used to determine any added functions to this interface, and will be called when object
    are received, if the type of incoming message matches the interface method parameter type.
    """
    @staticmethod
    @property
    def interfaceInfo():
        """Information object of the interface for this ConnectionHandler
        """
        raise NotImplementedError

    @abstractmethod
    def onSuspend(self):
        """Marks the connection to be suspended. The connection will be reinstated when at least one of the processes
        belonging to the connection is moved to a new node. After suspending {@link #resumeAfterSuspend()} will be
        called to reinstate the connection between the processes.
        """
        raise NotImplementedError

    @abstractmethod
    def resumeAfterSuspend(self):
        """Called when a connection between processes is reinstated after a suspend action.
        """
        raise NotImplementedError

    @abstractmethod
    def onInterrupt(self):
        """Marks the connection to be interrupted. The connection is supposed to resume when the origin of the failure
        is handled. After interrupting {@link #resumeAfterInterrupt()} is called when the processes should resume
        communication.
        """
        raise NotImplementedError

    @abstractmethod
    def resumeAfterInterrupt(self):
        """Called when the connection is interrupted, but the origin of the interruption is handled.
        """
        raise NotImplementedError

    @abstractmethod
    def terminated(self):
        """Marks the connection to be terminated. This means the connection will be destroyed and not be reinstated in
        the future.
        """
        raise NotImplementedError

