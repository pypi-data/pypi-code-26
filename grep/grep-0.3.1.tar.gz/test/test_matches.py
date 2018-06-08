from grep.internals import Matches, Context
from lazyme.string import color_str


def test_sanity():
    matches = Matches(
        """A
B
C
D
A
B
C
D""",
        Context(),
        "A",
    )

    assert tuple(matches) == ("A", "A")


def test_line_numbering():
    matches = Matches(
        """A
B
C
D
A
B
C
D""",
        Context(),
        "A",
        number_lines=True,
    )

    assert tuple(matches) == ("1: A", "5: A")


def test_before():
    matches = Matches(
        """A
B
C
D
A
B
C
D""",
        Context(before=1),
        "A",
        number_lines=True,
    )

    assert set(matches.matching_lines()) == {0, 4, 3}


def test_after():
    matches = Matches(
        """A
B
C
D
A
B
C
D""",
        Context(after=1),
        "A",
        number_lines=True,
    )

    assert set(matches.matching_lines()) == {0, 1, 4, 5}


def test_context():
    matches = Matches(
        """A
    B
    C
    D
    A
    B
    C
    D""",
        Context(context=2),
        "A",
        number_lines=True,
    )

    assert set(matches.matching_lines()) == {0, 1, 2, 3, 4, 5, 6}


def test_zero_based():
    matches = Matches("A", Context(), "A", zero_based=True, number_lines=True)
    assert tuple(matches) == ("0: A",)


def test_only_matched():
    matches = Matches("ABCDE", Context(), "B.D", only_matched=True)
    assert tuple(matches) == ("BCD",)


def test_color():
    matches = Matches("ABCDE", Context(), "B.D", color="red")
    assert tuple(matches) == (color_str("ABCDE", "red"),)


def test_context_is_not_colored():
    matches = Matches(
        """ABCDE
MEOW""",
        Context(after=1),
        "B.D",
        color="red",
    )
    assert tuple(matches) == (color_str("ABCDE", "red"), "MEOW")
