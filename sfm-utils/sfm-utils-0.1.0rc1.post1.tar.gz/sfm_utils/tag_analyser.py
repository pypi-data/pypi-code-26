import unicodedata
import re
from .type_deductor import TypeDeductor, AggregateTypeDeductor
from .tag_value_collection import TypeDeducingValueCollection, UniqueValueCollection


class TypeDeducingValueCollectionFactory(object):
    """Factory for constructing TypeDeducingValueCollection objects.

    TypeDeducingValueCollection objects will be constructed with a
    pre-defined list of type deduction rules. The type deduction rules
    are determined by the configured properties of the Factory.

    The Factory is a functor; construct a TypeDeducingValueCollection
    by calling the factory:
        factory = TypeDeducingValueCollectionFactory(...)
        value_collection = factory()

    """
    def __init__(self, count, strictness=1.0):
        """Initialise the TypeDeducingValueCollectionFactory.

        Args:
            count: int
                The number of values that are expected to be collected

            strictness: float, optional
                A sensitivity factor applied to type deduction rules.

                If greater than 1 then type deduction rules are less
                strict.
                If less than 1 then type deduction rules are stricter.

        """
        # sanitise inputs:
        # strictness of 0 or less is ignored
        if strictness <= 0:
            strictness = 1
        # count must be greater than 0
        if count <= 0:
            count = 1

        self._count = count
        self._strictness = strictness

    def __call__(self):
        """Construct a TypeDeducingValueCollection."""
        # values should be normalized
        normalizer = lambda v: unicodedata.normalize("NFC", v)

        # if all other type deduction fails, assume nullable text
        defaultType = self._textTypeDeductor(
            "optional text", nullable=True)
        defaultType.threshold = 0

        # populate the type deduction rules
        return TypeDeducingValueCollection([
            self._nullTypeDeductor("NULL type"),
            self._numberTypeDeductor("number", nullable=False),
            self._numberTypeDeductor("optional number", nullable=True),
            self._enumeratedTermTypeDeductor("enumeration", nullable=False),
            self._enumeratedTermTypeDeductor("optional enumeration", nullable=True),
            self._wordTypeDeductor("word", nullable=False),
            self._wordTypeDeductor("optional word", nullable=True),
            self._singleTermTypeDeductor("phrase", nullable=False),
            self._singleTermTypeDeductor("optional phrase", nullable=True),
            # self._wordListTypeDeductor("word list", nullable=False),
            self._enumeratedTermListTypeDeductor("enumeration list", nullable=False),
            self._textTypeDeductor("text", nullable=False),
            defaultType,  # optional text, threshold=0
            ],
            value_formatter=normalizer
        )

    def _nullTypeDeductor(self, name):
        """A TypeDeductor to detect NULL values."""
        return TypeDeductor(
            name,
            lambda v: v is None,
            threshold=self._adjusted_threshold(1)
        )

    def _numberTypeDeductor(self, name, nullable=False):
        """A TypeDeductor to detect numeric values."""
        nullReturn = nullable
        return TypeDeductor(
            name,
            lambda v: self.is_number(v) if v else nullReturn,
            threshold=self._adjusted_threshold(5)
        )

    def _wordTypeDeductor(self, name, nullable=False):
        """A TypeDeductor to detect single-word values."""
        nullReturn = nullable
        return TypeDeductor(
            name,
            lambda v: self.is_word(v) if v else nullReturn,
            threshold=self._adjusted_threshold(5)
        )

    def _singleTermTypeDeductor(self, name, nullable=False):
        """A TypeDeductor to detect single-term values."""
        nullReturn = nullable
        return TypeDeductor(
            name,
            lambda v: self.is_single_term(v) if v else nullReturn,
            threshold=self._adjusted_threshold(5)
        )

    def _termListTypeDeductor(self, name, nullable=False):
        """A TypeDeductor to detect list-of-term values."""
        nullReturn = nullable
        return TypeDeductor(
            name,
            lambda v: self.is_term_list(v) if v else nullReturn,
            threshold=self._adjusted_threshold(5)
        )

    def _textTypeDeductor(self, name, nullable=False):
        """A TypeDeductor to detect any values."""
        nullReturn = nullable
        return TypeDeductor(
            name,
            lambda v: True if v else nullReturn,
            threshold=self._adjusted_threshold(3))

    def _enumeratedTermTypeDeductor(self, name, nullable=False):
        """A TypeDeductor to detect single-item values where the
        values are selected from a set of known terms.

        Returns true if the number of distinct values over the whole
        collection is less than some proportion of the total number
        of values.

        """
        termDeductor = self._singleTermTypeDeductor(name, nullable)  # used as template
        enumerationDeductor = AggregateTypeDeductor(
            termDeductor.typename,
            termDeductor.deduction_rule,
            lambda known_values: len(known_values) < self._enumeration_threshold(),
            threshold=termDeductor.threshold)
        enumerationDeductor.instance_collection = UniqueValueCollection()
        enumerationDeductor.example_collection = UniqueValueCollection()
        return enumerationDeductor

    def _enumeratedTermListTypeDeductor(self, name, nullable=False):
        """A TypeDeductor to detect multi-item values where the
        values are selected from a set of known terms.

        Returns true if the number of distinct term values over the
        whole collection is less than some proportion of the total
        number of terms.

        """
        termListDeductor = self._termListTypeDeductor(name, nullable)  # used as template
        enumerationDeductor = AggregateTypeDeductor(
            termListDeductor.typename,
            termListDeductor.deduction_rule,
            lambda known_values: len(known_values) < self._enumeration_threshold(),
            threshold=termListDeductor.threshold)
        def split_terms(term_list):
            if term_list is None:
                return None
            return re.split(r"(\s*,\s*)+", term_list)
        enumerationDeductor.instance_collection = UniqueValueCollection(
            value_formatter=split_terms)
        enumerationDeductor.example_collection = UniqueValueCollection(
            value_formatter=split_terms)
        return enumerationDeductor

    def _adjusted_threshold(self, threshold_value):
        return (threshold_value * self._strictness)

    def _enumeration_threshold(self, limit=200, slope_factor=300):
        """Statistical threshold to determine a set of known words.

        Examples: (with limit=200 and slope_factor=300)
           Total values   Threshold (maximum allowed distinct values)
              5                 3
             20                12
             50                28
            100                50
           1000               153
           2000               173
           5000               188
          10000               194

        """
        # using L as limit, and K as slope:
        # f(x) = (L*x/K) * (1 - x/(x+K))
        # tends to L at a rate determined by K.
        # Furthermore, if K >= L then f(x) is always < x
        L = limit
        K = slope_factor
        x = self._count
        threshold = int((L*x/K) * (1 - x/(x+K)))
        # print("Enumeration threshold for set of {} values = {}".format(x, threshold))
        return threshold

    @staticmethod
    def is_number(value):
        return value.isdecimal()

    @staticmethod
    def is_word(value):
        # value should previously have been normalized using unicodedata.normalize("NFC",...)
        # false if there is whitespace, period, comma or semicolon within the text
        # (a single trailing period, comma or semicolon is OK)
        # also, there must be at least one alphanumeric character in the text.
        regex = r"[^\s\w.,;]*\w[^\s.,;]*.?(\s*[,;]\s*)?"
        match = re.fullmatch(regex, value.strip())
        return match is not None

    @staticmethod
    def is_single_term(value):
        # like is word, but may include whitespace;
        # false if there is a period, comma or semicolon within the text
        regex = r"[^\w.,;]*\w[^.,;]*.?(\s*[;,]\s*)?"
        match = re.fullmatch(regex, value.strip())
        return match is not None

    @staticmethod
    def is_term_list(value):
        # value should previously have been normalized using unicodedata.normalize("NFC",...)
        # true if the text comprises terms separated by commas or semicolons
        # terms are allowed to end with a period, in case of abbreviations
        regex = r"([^\w.,;]*\w[^.,;]*.?\s*[,;]\s*)*[^\w.,;]*\w[^.,;]*.?(\s*[,;]\s*)?"
        match = re.fullmatch(regex, value.strip())
        return match is not None


class TagCollection(object):
    """A dictionary-like collection of tags with associated tag info."""

    def __init__(self, label_dictionary={}):
        """Initialize the tag collection.

        Args:
            label_dictionary : dict, optional
               A lookup table for tag labels (e.g. '\lx': 'lexeme')

        """
        self._known_labels = label_dictionary
        self._tags = {}
        self._value_collection_factory = None

    @property
    def value_collection_factory(self):
        return self._value_collection_factory

    @value_collection_factory.setter
    def value_collection_factory(self, factory):
        self._value_collection_factory = factory

    def add(self, tag, value, context=None):
        # get the existing tag details, or create a new tag record
        if tag not in self._tags:
            self._tags[tag] = {
                'count': 0,
                'label': self._lookup(tag),
                'values': self._create_value_collection(),
                'first occurrence': context,
            }
        t = self._tags[tag]
        # record this tag occurrence
        t['count'] += 1
        t['last occurrence'] = context
        # process the value
        value_collection = t['values']
        if value_collection is not None:
            value_collection.add(value, context)

    def _lookup(self, tag):
        UNKNOWN_TAG_LABEL = "???"
        return self._known_labels.get(tag, UNKNOWN_TAG_LABEL)

    def _create_value_collection(self):
        if self._value_collection_factory:
            return self._value_collection_factory()
        return None

    def __getitem__(self, index):
        return self._tags[index]

    def __iter__(self):
        items = self._tags.items()
        return iter(items)

    def __len__(self):
        return len(self._tags)

    def __str__(self):
        return str(self._tags)


class TagAnalyser(object):
    def __init__(self, tag_dictionary=None, strictness=1.0):
        self._tag_dictionary = tag_dictionary
        self._strictness_modifier = strictness

    def analyse(self, filename):
        # first-pass analysis to count the number of ocurrences of each tag
        # (allows better calculation of type deduction strictness per tag)
        tags = TagCollection(self._tag_dictionary)
        with (open(filename, encoding='utf8')) as f:
            for line in f:
                tag, value = self._parse_line(line)
                if tag:
                    tags.add(tag, value)

        # construct a value collection factory per tag type
        factory_lookup = dict(
            (tag, self._get_value_collection_factory(tag, info)) for (tag, info) in tags
        )

        # second-pass analysis performs type deduction
        analysed_tags = TagCollection(self._tag_dictionary)
        with (open(filename, encoding='utf8')) as f:
            for (i, line) in enumerate(f):
                tag, value = self._parse_line(line)
                if tag:
                    analysed_tags.value_collection_factory = factory_lookup[tag]
                    context = {'filename': filename, 'line_number': i+1}
                    analysed_tags.add(tag, value, context)
        return analysed_tags

    def _calculate_type_deduction_strictness(self, tag_count):
        """Calculate an appropriate strictness for each tag based on number of occurrences."""
        if (tag_count > 20):
            # type deductor threshold is treated as a percentage:
            # e.g. threshold / 100 * count,
            # modified by strictness_modifier
            strictness = tag_count/100*self._strictness_modifier
        elif (tag_count > 5):
            # type deductor threshold is treated as an absolute value
            strictness = 1
        else:
            # for a very small number of occurrences, all type deductor
            # thresholds will be in the range (0,1]
            # TODO - get maximum threshold value from type deductor
            # factory and return the reciprocal (i.e. 1/x)
            strictness = 0.2
        return strictness

    def _get_value_collection_factory(self, tag, info):
        """Get a configured TypeDeducingValueCollectionFactory."""
        count = info['count']
        s = self._calculate_type_deduction_strictness(count)
        # print ("Strictness for tag {}: {}".format(tag, s))
        return TypeDeducingValueCollectionFactory(count, s)

    @staticmethod
    def _parse_line(line):
        """Parse a line from an SFM file into a tag and a value."""
        line = line.strip()
        # ignore blank lines
        if (not line):
            return None, None
        # ignore comment lines
        if (line[0] == '#'):
            return None, None
        # split the line into tag, value parts
        parsed = iter(line.split(maxsplit=1))
        tag = next(parsed, None)
        value = next(parsed, None)
        return tag, value
