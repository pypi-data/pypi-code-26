from abc import ABC, abstractmethod
from . import conditions_combinations as combinations


class Condition(ABC):
    """Base interface of conditions"""
    @abstractmethod
    def __call__(self, context):
        """Execute condition

        Args:
            context (dict): execution context

        Returns:
            bool
        """

    def __and__(self, other):
        """Combine current condition with another one using the & operator

        Returns:
            AndCondition
        """
        return combinations.AndCondition([self, other])

    def __or__(self, other):
        """Combine current condition with another one using the | operator

        Returns:
            OrCondition
        """
        return combinations.OrCondition([self, other])


class StaticCondition(Condition):
    def __init__(self, value):
        """
        Args:
            value (bool): value returned by condition
        """
        self._value = value

    def __call__(self, context):
        """Execute condition

        Args:
            context (dict): execution context

        Returns:
            bool
        """
        return self._value


class FalseCondition(StaticCondition):
    """Condition that always return False"""
    def __init__(self):
        super().__init__(False)


class TrueCondition(StaticCondition):
    """Condition that always return True"""
    def __init__(self):
        super().__init__(True)
