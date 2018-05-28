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

from numpy.testing import assert_array_equal

from rama import read, is_template
from rama.models.cube import NDPoint, Observable
from rama.models.measurements import StdPosition
from rama.tools.time import TimeSeries


@pytest.fixture
def time_series(make_data_path):
    return read(make_data_path('time-series.vot.xml'))

def test_is_template(time_series, recwarn):
    gavo = time_series
    positions = gavo.find_instances(StdPosition)
    cube_points = gavo.find_instances(NDPoint)
    axes = gavo.find_instances(Observable)

    assert not is_template(positions[0])  # positions are direct
    assert is_template(cube_points[0])  # ndpoint is a template
    assert is_template(axes[0])  # time
    assert not is_template(axes[1])  # position
    assert is_template(axes[2])  # magnitude
    assert is_template(axes[3])  # flux

    assert not is_template(gavo)  # an unrelated instance is never a template

    assert "W20" in str(recwarn[0].message)
    assert "W41" in str(recwarn[1].message)
    for i in range(2, 12):
        assert "W10" in str(recwarn[i].message)


def test_time_series(time_series, recwarn):
    cube_point = time_series.find_instances(NDPoint)[0]
    time_series = TimeSeries(cube_point)

    assert_array_equal(time_series.time, cube_point['hjd'])
    assert_array_equal(time_series['time'], cube_point['hjd'])
    assert_array_equal(time_series.dependent[0], cube_point['flux'])
    assert_array_equal(time_series['flux'], cube_point['flux'])

    assert "W20" in str(recwarn[0].message)
    assert "W41" in str(recwarn[1].message)
    for i in range(2, 12):
        assert "W10" in str(recwarn[i].message)