from abc import abstractmethod

from defpi.DefPiParameters import DefPiParameters


class Service:

    @abstractmethod
    def resumeFrom(self, state):
        """This function is only called if this instance is the resumed version of an old process. It is called with the
        serialized process state, which was returned from the {@link #suspend()} function. This function is called
        *before* the init function, if it is a resumed instance of an earlier process.
        """
        raise NotImplementedError

    @abstractmethod
    def init(self, config: dict, parameters: DefPiParameters):
        """This function is called after the constructor (or immediately after the resumeFrom function if applicable),
        when the configuration is first available. This method is only called once, and after it, the service is
        considered to be "running"."""
        raise NotImplementedError

    @abstractmethod
    def modify(self, config: dict):
        """This function is called when the configuration changes during runtime. It may be called multiple times.
        """
        raise NotImplementedError

    @abstractmethod
    def suspend(self):
        """Marks that this process is about to be suspended. This means the object *will* be destroyed, and may be
        subsequently created in another iteration. Any data has to be stored now.
        """
        raise NotImplementedError

    @abstractmethod
    def terminate(self):
        """Marks that this process is about to be terminated. This means the object *will* be destroyed.
        """
        raise NotImplementedError
