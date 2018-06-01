import gravity as grv


class BlockchainInstance():
    """ This is a class that allows compatibility with previous
        naming conventions
    """
    def __init__(self, *args, **kwargs):
        if "gravity_instance" in kwargs and kwargs["gravity_instance"]:
            self.blockchain = kwargs["gravity_instance"]
        elif "blockchain_instance" in kwargs and kwargs["blockchain_instance"]:
            self.blockchain = kwargs["blockchain_instance"]
        else:
            if kwargs:
                set_shared_config(kwargs)
            self.blockchain = shared_blockchain_instance()

    @property
    def Gravity(self):
        """ Alias for the specific blockchain
        """
        return self.blockchain

    @property
    def chain(self):
        """ Short form for blockchain (for the lazy)
        """
        return self.blockchain


class SharedInstance():
    """ This class merely offers a singelton for the Blockchain Instance
    """
    instance = None
    config = {}


def shared_blockchain_instance():
    """ This method will initialize ``SharedInstance.instance`` and return it.
        The purpose of this method is to have offer single default
        gravity instance that can be reused by multiple classes.
    """
    if not SharedInstance.instance:
        clear_cache()
        SharedInstance.instance = grv.Gravity(**SharedInstance.config)
    return SharedInstance.instance


def set_shared_blockchain_instance(gravity_instance):
    """ This method allows us to override default gravity instance for all
        users of ``SharedInstance.instance``.

        :param gravity.gravity gravity_instance: gravity
            instance
    """
    clear_cache()
    SharedInstance.instance = gravity_instance


def clear_cache():
    """ Clear Caches
    """
    from .blockchainobject import BlockchainObject
    BlockchainObject.clear_cache()


def set_shared_config(config):
    """ This allows to set a config that will be used when calling
        ``shared_gravity_instance`` and allows to define the configuration
        without requiring to actually create an instance
    """
    assert isinstance(config, dict)
    SharedInstance.config.update(config)


shared_gravity_instance = shared_blockchain_instance
set_shared_gravity_instance = set_shared_blockchain_instance
