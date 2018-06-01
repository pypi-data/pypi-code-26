from set_algebra.infinity import Infinity, NegativeInfinity, inf, neg_inf, is_finite
from set_algebra.parser import (EXCLUDED_OPEN_TO_BOUNDS_MAPPING, parse_bound,
    parse_endpoint_notation)


class Endpoint(object):
    """
    Class representing point on an axis. Can be of four kinds:
        [1      Not excluded open 
        (1      Excluded open
        1]      Not excluded closed
        1)      Excluded closed

    There are 2 ways to instantiate Endpoint:

    - From notation string (for numeric values only):
        Endpoint('[1'), Endpoint('-0.6)'), Endpoint('3.4e-5'), Endpoint('(-inf')

    - From value and bound character
        Endpoint(3, ']'), Endpoint(datetime.date.today(), '(')

    Endpoints can be compared with scalars and endpoints.
    Endpoints support bitwise inversion:
    ~Endpoint('[7') -> Endpoint('7)')

    To give an idea how Endpoint can be compared to other Endpoint or scalar,
    the figure below demonstrates some Endpoints located on the real axis:
           (0                   1)  1]  (1                   2)
                                   [1
        0                           1                            2
    ------------------------------------------------------------------------->

    See tests/test_endpoint.py for details.
    """

    __slots__ = ('value', 'excluded', 'open')

    PARSABLE_TYPES = (int, float, Infinity, NegativeInfinity)

    def __init__(self, notation_or_value, bound=None):
        if bound is None:
            value, excluded, open = parse_endpoint_notation(notation_or_value)
        else:
            value = notation_or_value
            excluded, open = parse_bound(bound)

        if not excluded and not is_finite(value):
            raise ValueError('Not excluded value cannot be infinite, use "(" or ")" as bound')

        self.value = value
        self.excluded = excluded
        self.open = open

    @property
    def closed(self):
        return not self.open

    @property
    def notation(self):
        if self.open:
            _format = self.excluded and '(%s' or '[%s'
        else:
            _format = self.excluded and '%s)' or '%s]'
        value_str = self.value == neg_inf and '-inf' or str(self.value)
        return _format % value_str

    def __repr__(self):
        classname = type(self).__name__
        if isinstance(self.value, self.PARSABLE_TYPES):
            repr_format = "%s('%s')"
            params = (classname, self.notation)
        else:
            repr_format = "%s(%s, '%s')"
            bound = EXCLUDED_OPEN_TO_BOUNDS_MAPPING[self.excluded, self.open]
            params = (classname, repr(self.value), bound)
        return repr_format % params

    def __eq__(self, other):
        """
        self == other
        When comparing two Endpoints,
            test whether all 3 slots (value, excluded, open) are equal.
        When other is not Endpoint test whether Endpoint value is equal to the other,
            and if Endpoint is not excluded:
        >>> Endpoint('[1') == 1
        True
        >>> Endpoint('(1') == 1
        False
        """
        if isinstance(other, Endpoint):
            return self.value == other.value \
               and self.excluded == other.excluded \
               and self.open == other.open
        else:
            return not self.excluded and self.value == other

    def __ne__(self, other):
        """ self != other """
        return not self == other

    def __gt__(self, other):
        """ self > other """
        if isinstance(other, Endpoint):
            if self.value == other.value:
                return self._cmp(other) == 1
            else:
                return self.value > other.value
        else:
            if self.value == other:
                return self.excluded and self.open
            else:
                return self.value > other

    def __ge__(self, other):
        """ self >= other """
        if isinstance(other, Endpoint):
            if self.value == other.value:
                return self._cmp(other) != -1
            else:
                return self.value > other.value
        else:
            if self.value == other:
                return not self.excluded or self.open
            else:
                return self.value > other

    def __lt__(self, other):
        """ self < other """
        if isinstance(other, Endpoint):
            if self.value == other.value:
                return self._cmp(other) == -1
            else:
                return self.value < other.value
        else:
            if self.value == other:
                return self.excluded and self.closed
            else:
                return self.value < other

    def __le__(self, other):
        """ self <= other """
        if isinstance(other, Endpoint):
            if self.value == other.value:
                return self._cmp(other) != 1
            else:
                return self.value < other.value
        else:
            if self.value == other:
                return not self.excluded or self.closed
            else:
                return self.value < other

    def _cmp(self, other):
        """Compare two Endpoints with equal values."""
        if self.open:
            if other.open:
                if not self.excluded and not other.excluded:
                    return 0
                if not self.excluded and other.excluded:
                    return -1
                if self.excluded and not other.excluded:
                    return 1
                else:
                    return 0
            else:
                if not self.excluded and not other.excluded:
                    return 0
                else:
                    return 1
        else:
            if other.open:
                if not self.excluded and not other.excluded:
                    return 0
                else:
                    return -1
            else:
                if not self.excluded and not other.excluded:
                    return 0
                if not self.excluded and other.excluded:
                    return 1
                if self.excluded and not other.excluded:
                    return -1
                else:
                    return 0

    def __invert__(self):
        """
        Return Endpoint with same value but opposite excluded and open attributes.
        >>> ~Endpoint('[1')
        Endpoint('1)')
        """
        bound = EXCLUDED_OPEN_TO_BOUNDS_MAPPING[not self.excluded, not self.open]
        return Endpoint(self.value, bound)

    def copy(self):
        """Return a shallow copy of the Endpoint"""
        bound = EXCLUDED_OPEN_TO_BOUNDS_MAPPING[self.excluded, self.open]
        return Endpoint(self.value, bound)


def are_bounding(e1, e2):
    """
    Return boolean indicating that 2 endpoints have no gap between them.
    >>> are_bounding(Endpoint('1]'), Endpoint('(1'))
    True
    >>> are_bounding(Endpoint('[1'), Endpoint('1]'))
    True
    >>> are_bounding(Endpoint('1)'), Endpoint('(1'))
    False
    """
    assert e1.open is not e2.open
    return e1.value == e2.value and (not e1.excluded or not e2.excluded)

