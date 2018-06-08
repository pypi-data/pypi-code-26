from grep.internals import Matches, Context, Pattern


def test_sanity():
    matches = Matches(
        """A
1
C
4
A
6
7
D""",
        Context(),
        Pattern("\d"),
    )

    assert tuple(matches) == ("1", "4", "6", "7")


def test_ignore_case():
    matches = Matches(
        """Hello
HELLO
HOW LOW
HALLOW""",
        Context(),
        Pattern("e", ignore_case=True),
    )

    assert tuple(matches) == ("Hello", "HELLO")


def test_words_only():
    matches = Matches(
        """Hello
Die today
Yes hello bye
effo
""",
        Context(),
        Pattern("e..o", words_only=True),
    )

    assert tuple(matches) == ("effo",)


def test_invert_match():
    matches = Matches(
        """Hello
HeLLO
HOW LOW
HALLOW""",
        Context(),
        Pattern("e", invert_match=True),
    )

    assert tuple(matches) == ("HOW LOW", "HALLOW")
