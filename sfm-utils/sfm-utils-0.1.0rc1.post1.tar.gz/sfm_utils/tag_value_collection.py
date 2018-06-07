import collections
import six


class UniqueValueCollection(object):
    def __init__(self, value_formatter=None):
        self._known_values = set()
        self._format = value_formatter

    def __len__(self):
        return len(self._known_values)

    def __str__(self):
        return ",".join(sorted(self._known_values))

    def add(self, value, context=None):
        if self._format is not None and value is not None:
            value = self._format(value)
        if (self._is_list_type(value)):  # if the value is iterable, add items individually
            for v in value:
                if v is not None:
                    self._known_values.add(v)
        elif value is not None:
            self._known_values.add(value) # not a sequence so simply add the value

    @staticmethod
    def _is_list_type(arg):
        return isinstance(arg, collections.Iterable) and not isinstance(arg, six.string_types)


class TypeDeducingValueCollection(object):
    def __init__(self, type_deduction_rules=[], value_formatter=None):
        self._type_deduction_rules = type_deduction_rules
        self._format_fn = value_formatter
        self._deduced_type = None

    @property
    def deduced_type(self):
        deduced = self._deduce_type()
        return deduced.typename if deduced else None

    @property
    def examples(self):
        deduced = self._deduce_type()
        return deduced.example_collection if deduced else []

    @property
    def type_violations(self):
        deduced = self._deduce_type()
        return deduced.type_violations if deduced else []

    def add(self, value, context=None):
        self._format_value(value)
        for deductor in self._type_deduction_rules:
            deductor.apply(value, context)
        self._deduced_type = None

    def _format_value(self, value):
        if self._format_fn is None or value is None:
            return value
        # apply formatting to value
        return self._format_fn(value)

    def _deduce_type(self):
        if self._deduced_type is None:
            matched_rules = (
                rule for rule in self._type_deduction_rules
                if rule.is_valid
            )
            self._deduced_type = next(matched_rules, None)
        return self._deduced_type
