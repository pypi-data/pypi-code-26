class Singleton(type):
    """Metaclass used to generate singletons.
    """
    def __init__(cls, name, bases, attr, **kwargs):
        super().__init__(name, bases, attr)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        """Prevents multiple instances by returning a reference to the first one instantiated."""
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance
