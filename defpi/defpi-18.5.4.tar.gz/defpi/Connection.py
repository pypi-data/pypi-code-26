from abc import abstractmethod


class Connection:

    @abstractmethod
    def send(self, message):
        """Sends message over the connection to the other process
        """
        raise NotImplementedError

    # @abstractmethod
    # def isConnected(self): raise NotImplementedError

    @abstractmethod
    def getState(self):
        """Returns the state of the connection in the form of a Protocol Buffers enum
        (in defpi.protobufs.Connection_pb2).
        Possible values are:
        STARTING
        CONNECTED
        SUSPENDED
        INTERRUPTED
        TERMINATED
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def remoteProcessId(self):
        """Returns the remote process identifier of the current process
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def remoteServiceId(self):
        """Returns the remote service identifier of the service corresponding to the current process
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def remoteInterfaceId(self):
        """Returns the remote interface identifier corresponding to the interface of the service this connection is
        attached
        """
        raise NotImplementedError
