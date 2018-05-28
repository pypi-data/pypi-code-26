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
from astropy import units as u
from unittest import mock

import numpy as np
from numpy.testing import assert_array_equal

from rama.adapters.cube import CubePoint
from rama.models.measurements import StdTimeMeasure, GenericCoordMeasure
from rama.tools.time import TimeSeries


class TimeAxisStub:
    def __init__(self):
        self.dependent = False
        coord = np.array([1, 2, 3]) * u.Unit('d')
        coord.name = "foo"
        self.measure = mock.MagicMock(StdTimeMeasure, coord=coord)


class FluxAxisStub:
    def __init__(self):
        self.dependent = True
        cval = np.array([10, 20, 30]) * u.Unit('mag')
        cval.name = 'flux'
        coord = mock.MagicMock(cval=cval)
        self.measure = mock.MagicMock(GenericCoordMeasure, coord=coord)


class NdPointStub:
    observable = [TimeAxisStub(), FluxAxisStub()]


def test_time_series():
    cube = CubePoint(NdPointStub())
    time_series = TimeSeries(cube)

    assert_array_equal(time_series.time.measure, np.array([1, 2, 3]) * u.Unit('d'))
    assert_array_equal(time_series['time'].measure, np.array([1, 2, 3]) * u.Unit('d'))
    assert_array_equal(time_series.dependent[0].measure, np.array([10, 20, 30]) * u.Unit('mag'))
    assert_array_equal(time_series['flux'].measure, np.array([10, 20, 30]) * u.Unit('mag'))