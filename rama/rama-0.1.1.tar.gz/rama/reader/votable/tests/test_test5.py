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
import pytest
from astropy.table import MaskedColumn
from astropy import units as u
from numpy.testing import assert_array_equal

from rama import is_template, count, unroll
from rama.models.test.filter import PhotometryFilter
from rama.models.test.sample import SkyCoordinateFrame, Source
from rama.reader import Reader
from rama.reader.votable import Votable


@pytest.fixture
def context_test5(make_data_path):
    return Reader(Votable(make_data_path("test5.vot.xml")))


def test_coordinate_frame(context_test5):
    frames = context_test5.find_instances(SkyCoordinateFrame)

    assert len(frames) == 1
    assert frames[0].name == "ICRS"


def test_filters(context_test5):
    filters = context_test5.find_instances(PhotometryFilter)

    assert len(filters) == 5
    assert filters[0].name == "2mass:H"
    assert filters[1].name == "2mass:J"
    assert filters[2].name == "2mass:K"
    assert filters[3].name == "sdss:g"
    assert filters[4].name == "sdss:r"


def test_source(context_test5, recwarn):
    sources = context_test5.find_instances(Source)

    assert len(sources) == 1
    source = sources[0]
    # assert_array_equal(source.id, [b'08120809-0206132', b'08115683-0205428', b'08115826-0205336'])
    # assert_array_equal(source.name, [b'08120809-0206132', b'08115683-0205428', b'08115826-0205336'])
    assert_array_equal(source.position.longitude, MaskedColumn([123.033734, 122.986794, 122.992773],
                                                               dtype='float32', unit='deg'))
    assert_array_equal(source.position.latitude, MaskedColumn([-2.103671, -2.095231, -2.092676],
                                                              dtype='float32', unit='deg'))

    frame = context_test5.find_instances(SkyCoordinateFrame)[0]
    filters = context_test5.find_instances(PhotometryFilter)
    h_filter = filters[0]
    j_filter = filters[1]
    k_filter = filters[2]

    assert source.position.frame is frame

    assert len(source.luminosity) == 3

    h_mag = source.luminosity[0]
    assert h_mag.type == 'magnitude'
    assert h_mag.filter is h_filter
    assert_array_equal(h_mag.value, MaskedColumn([13.681, 15.103, 15.718],
                                                 dtype='float32', unit='mag'))
    assert_array_equal(h_mag.error, MaskedColumn([0.027, 0.077, 0.112],
                                                 dtype='float32', unit='mag'))
    j_mag = source.luminosity[1]
    assert j_mag.type == 'magnitude'
    assert j_mag.filter is j_filter
    assert_array_equal(j_mag.value, MaskedColumn([14.161, 15.86, 16.273],
                                                 dtype='float32', unit='mag'))
    assert_array_equal(j_mag.error, MaskedColumn([0.025, 0.06, 0.096],
                                                 dtype='float32', unit='mag'))

    k_mag = source.luminosity[2]
    assert k_mag.type == 'magnitude'
    assert k_mag.filter is k_filter
    assert_array_equal(k_mag.value, MaskedColumn([13.675, 14.847, 15.46],
                                                 dtype='float32', unit='mag'))
    assert_array_equal(k_mag.error, MaskedColumn([0.048, 0.127, 0.212],
                                                 dtype='float32', unit='mag'))

    assert "W20" in str(recwarn[0].message)
    assert "W41" in str(recwarn[1].message)
    for i in range(2, 12):
        assert "W10" in str(recwarn[i].message)

    # TODO MISSING multi-table relationship


def test_source_unroll(context_test5, recwarn):
    template_source = context_test5.find_instances(Source)[0]
    assert is_template(template_source)
    assert count(template_source) == 3

    frame = context_test5.find_instances(SkyCoordinateFrame)[0]
    filters = context_test5.find_instances(PhotometryFilter)
    h_filter = filters[0]
    j_filter = filters[1]
    k_filter = filters[2]

    sources = unroll(template_source)

    assert len(sources) == 3
    source = sources[0]
    assert source.name == '08120809-0206132'
    assert source.position.longitude == template_source.position.longitude[0]
    assert source.position.latitude == template_source.position.latitude[0]
    assert source.position.frame is frame
    h_mag = source.luminosity[0]
    assert h_mag.type == 'magnitude'
    assert h_mag.filter is h_filter
    assert h_mag.value == template_source.luminosity[0].value[0]
    assert h_mag.error == template_source.luminosity[0].error[0]

    j_mag = source.luminosity[1]
    assert j_mag.type == 'magnitude'
    assert j_mag.filter is j_filter
    assert j_mag.value == template_source.luminosity[1].value[0]
    assert j_mag.error == template_source.luminosity[1].error[0]

    k_mag = source.luminosity[2]
    assert k_mag.type == 'magnitude'
    assert k_mag.filter is k_filter
    assert k_mag.value == template_source.luminosity[2].value[0]
    assert k_mag.error == template_source.luminosity[2].error[0]

    source = sources[1]
    assert source.name == '08115683-0205428'
    assert source.position.longitude == template_source.position.longitude[1]
    assert source.position.latitude == template_source.position.latitude[1]
    assert source.position.frame is frame
    h_mag = source.luminosity[0]
    assert h_mag.type == 'magnitude'
    assert h_mag.filter is h_filter
    assert h_mag.value == template_source.luminosity[0].value[1]
    assert h_mag.error == template_source.luminosity[0].error[1]

    j_mag = source.luminosity[1]
    assert j_mag.type == 'magnitude'
    assert j_mag.filter is j_filter
    assert j_mag.value == template_source.luminosity[1].value[1]
    assert j_mag.error == template_source.luminosity[1].error[1]

    k_mag = source.luminosity[2]
    assert k_mag.type == 'magnitude'
    assert k_mag.filter is k_filter
    assert k_mag.value == template_source.luminosity[2].value[1]
    assert k_mag.error == template_source.luminosity[2].error[1]

    source = sources[2]
    assert source.name == '08115826-0205336'
    assert source.position.longitude == template_source.position.longitude[2]
    assert source.position.latitude == template_source.position.latitude[2]
    assert source.position.frame is frame
    h_mag = source.luminosity[0]
    assert h_mag.type == 'magnitude'
    assert h_mag.filter is h_filter
    assert h_mag.value == template_source.luminosity[0].value[2]
    assert h_mag.error == template_source.luminosity[0].error[2]

    j_mag = source.luminosity[1]
    assert j_mag.type == 'magnitude'
    assert j_mag.filter is j_filter
    assert j_mag.value == template_source.luminosity[1].value[2]
    assert j_mag.error == template_source.luminosity[1].error[2]

    k_mag = source.luminosity[2]
    assert k_mag.type == 'magnitude'
    assert k_mag.filter is k_filter
    assert k_mag.value == template_source.luminosity[2].value[2]
    assert k_mag.error == template_source.luminosity[2].error[2]
