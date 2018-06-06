class Context(dict):
    """Object filled by resolvers when evaluating a rule
    It's mainly used to store a corresponding value from a parameter.

    Example:
        resolver will receive a user_id, then look for the corresponding user in DB
        and finally store the user into the context in order to let him be accessible
        in the condition
    """
    def __init__(self, args=(), kwargs=None):
        """
        Args:
            args (list): arguments received from ability caller
            kwargs (dict): keyword arguments received from ability caller
        """
        super().__init__()
        self.args = args
        self.kwargs = kwargs or {}
        for key, value in self.kwargs.items():
            self[key] = value

    def __setitem__(self, key, value):
        """Adding a key to context creates an attibute of the same name

        Args:
            key (str): a key
            value (object): value associated to key
        """
        setattr(self, key, value)

    def __setattr__(self, name, value):
        """Adding an attribute adds a corresponding entry into the dict

        Args:
            key (str): a key
            value (object): value associated to key
        """
        super().__setitem__(name, value)
        super().__setattr__(name, value)

    def update(self, other):
        for key, value in other.items():
            self[key] = value
