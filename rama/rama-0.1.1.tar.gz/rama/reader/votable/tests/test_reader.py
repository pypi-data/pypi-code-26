# Copyright 2018 Smithsonian Astrophysical Observatory
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
# disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import numpy
import pytest
from astropy import units as u
from astropy.coordinates import SkyCoord, FK5
from astropy.time import Time

from rama.framework import InstanceId
from rama.models.test.sample import Source

from rama.models.coordinates import SpaceFrame
from rama.models.measurements import StdPosition
from rama import read, unroll
from rama.models.photdmalt import PhotometryFilter
from rama.models.source import Detection


@pytest.fixture
def simple_position_file(make_data_path):
    return read(make_data_path('simple-position.vot.xml'))


@pytest.fixture
def simple_position_columns_file(make_data_path):
    return read(make_data_path('simple-position-columns.vot.xml'))


@pytest.fixture
def invalid_file(make_data_path):
    return read(make_data_path('invalid.vot.xml'))


@pytest.fixture
def references_file(make_data_path):
    return read(make_data_path('references.vot.xml'))


@pytest.fixture
def asymmetric_data_file(make_data_path):
    return read(make_data_path('asymmetric-2d-position.vot.xml'))


@pytest.fixture
def hsc_data_file(make_data_path):
    return read(make_data_path('hsc.vot.xml'))


def test_parsing_coordinates(simple_position_file):
    sky_positions = simple_position_file.find_instances(StdPosition)
    pos = sky_positions[0]

    assert 1 == len(sky_positions)
    assert isinstance(pos.coord, SkyCoord)
    assert pos.coord.ra == 10.34209135 * u.Unit('deg')
    assert pos.coord.dec == 41.13232112 * u.Unit('deg')
    assert isinstance(pos.coord.frame, FK5)
    assert pos.coord.equinox == Time("J1975")
    # FIXME How to set the reference position in astropy?
    # assert "TOPOCENTER" == pos.coord.frame.ref_position.position


def test_references_are_same_object(references_file):
    sky_positions = references_file.find_instances(StdPosition)

    assert sky_positions[0].coord.frame is sky_positions[1].coord.frame


def test_referred_built_only_once(references_file):
    frame = references_file.find_instances(SpaceFrame)[0]
    frame2 = references_file.find_instances(SpaceFrame)[0]
    sky_positions = references_file.find_instances(StdPosition)

    assert frame is frame2
    assert sky_positions[0].coord.frame is frame
    assert sky_positions[1].coord.frame is frame


def test_parsing_columns(simple_position_columns_file, recwarn):
    sky_positions = simple_position_columns_file.find_instances(StdPosition)
    position = sky_positions[0]

    assert 1 == len(sky_positions)
    expected_ra = numpy.array([10.0, 20.0], dtype='float32') * u.Unit('deg')
    expected_dec = numpy.array([11.0, 21.0], dtype='float32') * u.Unit('deg')
    numpy.testing.assert_array_equal(expected_ra, position.coord.ra)
    numpy.testing.assert_array_equal(expected_dec, position.coord.dec)

    assert "W20" in str(recwarn[0].message)
    assert "W41" in str(recwarn[1].message)
    for i in range(2, 12):
        assert "W10" in str(recwarn[i].message)


def test_attribute_multiplicity(asymmetric_data_file, recwarn):
    position = asymmetric_data_file.find_instances(StdPosition)[0]

    plus = position.error.stat_error.plus
    assert len(plus) == 2

    minus = position.error.stat_error.minus
    assert len(minus) == 2

    assert "Dangling reference" in str(recwarn[0].message)


def test_invalid_file(invalid_file):

    with pytest.warns(SyntaxWarning) as record:
        sky_positions = invalid_file.find_instances(StdPosition)
        assert "ID foo" in str(record[-1].message)
        assert "W50" in str(record[12].message)

    position = sky_positions[0]

    assert 1 == len(sky_positions)
    expected_ra = numpy.array([numpy.NaN, numpy.NaN])
    expected_dec = u.Quantity(numpy.array([11.0, 21.0]))
    numpy.testing.assert_array_equal(expected_ra, position.coord.ra)
    numpy.testing.assert_array_equal(expected_dec.value, position.coord.dec.value)


def test_references_orm(references_file, recwarn):
    sources = references_file.find_instances(Source)
    filters = references_file.find_instances(PhotometryFilter)

    f814w = None
    f606w = None

    for hsc_filter in filters:
        if hsc_filter.name == "F814W":
            f814w = hsc_filter
        else:
            f606w = hsc_filter

    source = sources[0]
    assert source.luminosity[0].filter[0] is f606w
    assert source.luminosity[0].filter[1] is f814w


def test_references_orm_unroll(references_file, recwarn):
    sources = references_file.find_instances(Source)
    filters = references_file.find_instances(PhotometryFilter)

    f814w = None
    f606w = None

    for hsc_filter in filters:
        if hsc_filter.name == "F814W":
            f814w = hsc_filter
        else:
            f606w = hsc_filter

    source = unroll(sources[0])
    assert source[0].luminosity[0].filter is f606w
    assert source[1].luminosity[0].filter is f814w


def test_references_orm_hsc(hsc_data_file, recwarn):
    sources = hsc_data_file.find_instances(Detection)
    filters = hsc_data_file.find_instances(PhotometryFilter)

    f814w = None
    f606w = None

    for hsc_filter in filters:
        if hsc_filter.name == "F814W":
            f814w = hsc_filter
        else:
            f606w = hsc_filter

    source = sources[0]
    assert source.luminosity[0].filter[0] is f814w
    assert source.luminosity[0].filter[1] is f606w
    assert source.luminosity[0].filter[2] is f606w
    assert source.luminosity[0].filter[3] is f606w
    assert source.luminosity[0].filter[4] is f606w
    assert source.luminosity[0].filter[5] is f606w
    assert source.luminosity[0].filter[6] is f606w


def test_references_orm_unroll_hsc(hsc_data_file, recwarn):
    sources = hsc_data_file.find_instances(Detection)
    filters = hsc_data_file.find_instances(PhotometryFilter)

    f814w = None
    f606w = None

    for hsc_filter in filters:
        if hsc_filter.name == "F814W":
            f814w = hsc_filter
        else:
            f606w = hsc_filter

    assert sources[0].cardinality == 7

    source = unroll(sources[0])
    assert source[0].luminosity[0].filter is f814w
    assert source[1].luminosity[0].filter is f606w
    assert source[2].luminosity[0].filter is f606w
    assert source[3].luminosity[0].filter is f606w
    assert source[4].luminosity[0].filter is f606w
    assert source[5].luminosity[0].filter is f606w
    assert source[6].luminosity[0].filter is f606w


def test_polymorphism(hsc_data_file, recwarn):
    # There is no explicit instantiation of Source in the hsc file, but there is and instantiation of Detection,
    # which is a subtype of Source.
    from rama.models.source import Source
    sources = hsc_data_file.find_instances(Source)

    assert sources[0].cardinality == 7
    assert isinstance(sources[0], Detection)
    assert isinstance(sources[0], Source)
