

class TypeDeductor(object):
    """Determine whether a set of values conform to a type.

    Applies a type deduction rule to a set of values to determine
    whether or not the values are valid for the type. Allows for
    inconsistencies in the set of values by applying a threshold;
    so long as the count of values that violate the type deduction
    rule remains below the threshold, the values may be considered to
    conform to that type.

    Keeps a record of values that violate the type deduction rule.
    May also record collected examples of values for the type.

    A type deduction rule is any callable that, given some value,
    returns True or False to indicate whether the value satisfies the
    rule.

    """
    def __init__(self, typename, deduction_rule, threshold=0):
        """Initialise a TypeDeductor.

        Args:
            typename: string
                The name of the type.

            deduction_rule: callable
                A callable that accepts a single argument and returns
                a boolean result.
                Typically a function or a lambda expression.

            threshold: int, optional
                The limit to the number of values that may violate
                the rule yet still be considered valid for the type.
                If 0 or unspecified then no limit is applied: the
                set of values will always match this type. May be
                useful to record any and all violations of the type.
                If 1, then the values will not conform to this type
                if any single value violates the type rule.
                If greater than 1 then the values will not conform to
                this type if the given number of values violate the
                type rule.

        """
        self._typename = typename
        self._deduction_rule = deduction_rule
        self._examples = None
        self._violations = []
        self._threshold = threshold

    @property
    def typename(self):
        return self._typename

    @property
    def deduction_rule(self):
        return self._deduction_rule

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        self._threshold = value

    @property
    def example_collection(self):
        return self._examples

    @example_collection.setter
    def example_collection(self, value):
        self._examples = value

    @property
    def type_violations(self):
        return self._violations

    @property
    def is_valid(self):
        """True if the set of values conform to the type, else False."""
        if self._threshold > 0:
            return (len(self._violations) < self._threshold)
        return True

    def apply(self, value, context=None):
        """Add a new value to the set of values being tested."""
        if not self.is_valid:
            # rule has already been violated too many times;
            # no need to process further values
            return
        # process the new value
        if self._deduction_rule(value) is False:
            self._violations.append({'value': value, 'context': context})
        elif self._examples is not None:
            self._examples.add(value, context)


class AggregateTypeDeductor(TypeDeductor):
    """Determine whether a set of values conform to a type.

    Extension of TypeDeductor that applies the type deduction rule to
    each individual value, then also applies an aggregate rule to the
    overall set of known values.

    """
    def __init__(self, typename, deduction_rule, aggregate_rule, threshold=0):
        super(AggregateTypeDeductor, self).__init__(typename, deduction_rule, threshold)
        self._aggregate_rule = aggregate_rule
        self._instances = None

    @property
    def instance_collection(self):
        return self._instances

    @instance_collection.setter
    def instance_collection(self, value):
        self._instances = value

    @property
    def is_valid(self):
        if not super(AggregateTypeDeductor, self).is_valid:
            return False
        return self._aggregate_rule(self._instances)

    def apply(self, value, context=None):
        super(AggregateTypeDeductor, self).apply(value, context)
        if self.is_valid and self._deduction_rule(value) is True:
            if self._instances is not None:
                # print("AggregateTypeDeductor recording value {}".format(value))
                self._instances.add(value, context)

