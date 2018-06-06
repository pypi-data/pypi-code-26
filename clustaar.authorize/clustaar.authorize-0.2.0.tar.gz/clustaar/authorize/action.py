class Action(object):
    """
    Represents an action that `Ability` can allow or forbid access to.
    """
    def __init__(self, name):
        """
        Args:
            name (str): the action name
        """
        self.name = name
