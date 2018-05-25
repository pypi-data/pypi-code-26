import abjad
from abjadext import rmakers


def test_NoteRhythmMaker___call___01():

    maker = rmakers.NoteRhythmMaker()

    divisions = [(5, 16), (3, 8)]
    result = maker(divisions)

    maker = abjad.MeasureMaker()
    measures = maker(divisions)
    staff = abjad.Staff(measures)
    abjad.mutate(staff).replace_measure_contents(result)

    assert format(staff) == abjad.String.normalize(
        r"""
        \new Staff
        {
            {   % measure
                \time 5/16
                c'4
                ~
                c'16
            }   % measure
            {   % measure
                \time 3/8
                c'4.
            }   % measure
        }
        """
        )


def test_NoteRhythmMaker___call___02():

    duration_specifier = rmakers.DurationSpecifier(
        decrease_monotonic=False,
        )
    maker = rmakers.NoteRhythmMaker(
        duration_specifier=duration_specifier,
        )

    divisions = [(5, 16), (3, 8)]
    result = maker(divisions)

    maker = abjad.MeasureMaker()
    measures = maker(divisions)
    staff = abjad.Staff(measures)
    abjad.mutate(staff).replace_measure_contents(result)

    assert format(staff) == abjad.String.normalize(
        r"""
        \new Staff
        {
            {   % measure
                \time 5/16
                c'16
                ~
                c'4
            }   % measure
            {   % measure
                \time 3/8
                c'4.
            }   % measure
        }
        """
        )
