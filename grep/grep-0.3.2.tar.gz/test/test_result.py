from grep.internals import Result, Matches, Context


def test_result_hides_empty_matches():
    result = Result(Matches("HELLO", Context(context=1), pattern="NO_MATCH", only_matched=True))
    assert str(result) == ""
