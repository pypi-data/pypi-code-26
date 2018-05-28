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
from astropy.coordinates import SkyCoord
from astropy.table import MaskedColumn
from astropy.time import Time
from dateutil.parser import parse
from numpy.testing import assert_array_equal
from rama.models.dataset import ObsDataset

from rama.models.cube import NDPoint
from rama.reader import Reader
from rama.reader.votable import Votable


@pytest.fixture
def context_cube(make_data_path):
    return Reader(Votable(make_data_path("cube.vot.xml")))


def test_ndpoint(context_cube, recwarn):
    ndpoints = context_cube.find_instances(NDPoint)
    ndpoint = ndpoints[0]

    assert len(ndpoints) == 1

    assert_array_equal(ndpoint.dependent, ['flux', 'mag'])
    assert_array_equal(ndpoint.independent, ['time', 'position'])
    assert isinstance(ndpoint['position'].measure, SkyCoord)
    assert isinstance(ndpoint['time'].measure, Time)
    assert isinstance(ndpoint['mag'].measure, MaskedColumn)
    assert isinstance(ndpoint['flux'].measure, MaskedColumn)

    assert "W20" in str(recwarn[0].message)
    assert "W41" in str(recwarn[1].message)
    for i in range(2, 12):
        assert "W10" in str(recwarn[i].message)


def test_dataset(context_cube):
    datasets = context_cube.find_instances(ObsDataset)
    dataset = datasets[0]

    assert len(datasets) == 1
    assert dataset.data_product_type == 'TIMESERIES'
    assert dataset.calib_level == 3
    assert dataset.data_id.date == parse("2017-03-27T15:35:56")

    assert dataset.data_id.__parent__ is dataset

# def test_ext_instances(context_cube, recwarn):
#     cube = context_cube.find_instances(SparseCube)[0]
#
#     assert len(cube.data) == 1
#     assert len(cube.data[0].axis) == 4
#
#     assert "W20" in str(recwarn[0].message)
#     assert "W41" in str(recwarn[1].message)
#     for i in range(2, 12):
#         assert "W10" in str(recwarn[i].message)
