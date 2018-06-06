from .conditions import FalseCondition, TrueCondition


class AccessRule(object):
    """A rule is composed of a resolver and a condition.
    The resolvers are executed first is order to provide the data objects
    required by the condition.
    """
    def __init__(self, resolvers=(), condition=FalseCondition()):
        """
        Args:
            resolvers (list<callable>): list of resolvers
            condition (Condition): a condition
        """
        self._resolvers = resolvers
        self._condition = condition

    def __call__(self, context):
        """Returns whether or not if rules allows action

        Args:
            context (Context): a context

        Returns:
            bool
        """
        for resolver in self._resolvers:
            resolver(context)

        return self._condition(context)


class Deny(AccessRule):
    """Condition that always deny access"""
    def __init__(self):
        super().__init__(condition=FalseCondition())


class Allow(AccessRule):
    """Condition that always allows access"""
    def __init__(self):
        super().__init__(condition=TrueCondition())


ALLOW = Allow()
DENY = Deny()
