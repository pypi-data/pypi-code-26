from clustaar.authorize import conditions


class AndCondition(object):
    """Represents an & combination of conditions.
    It returns True when all conditions returns True
    """
    def __init__(self, conditions):
        """
        Args:
            conditions list<Condition>: a list of condition
        """
        self._conditions = conditions

    def __call__(self, params):
        for condition in self._conditions:
            if not condition(params):
                return False

        return True

    def __and__(self, other):
        if isinstance(other, AndCondition):
            self._conditions.extend(other._conditions)
            return self
        elif isinstance(other, conditions.Condition):
            self._conditions.append(other)
            return self

        return AndCondition([self, other])

    def __or__(self, other):
        return OrCondition([self, other])


class OrCondition(object):
    """Represents an | combination of conditions.
    It returns True when at least one condition returns True
    """
    def __init__(self, conditions):
        """
        Args:
            conditions list<Condition>: a list of condition
        """
        self._conditions = conditions

    def __call__(self, params):
        for condition in self._conditions:
            if condition(params):
                return True

        return False

    def __and__(self, other):
        return AndCondition([self, other])

    def __or__(self, other):
        if isinstance(other, OrCondition):
            self._conditions.extend(other._conditions)
            return self
        elif isinstance(other, conditions.Condition):
            self._conditions.append(other)
            return self

        return OrCondition([self, other])
