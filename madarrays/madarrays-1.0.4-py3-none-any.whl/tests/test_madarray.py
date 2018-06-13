# -*- coding: utf-8 -*-
# ######### COPYRIGHT #########
#
# Copyright(c) 2018
# -----------------
#
# * Laboratoire d'Informatique et Systèmes <http://www.lis-lab.fr/>
# * Université d'Aix-Marseille <http://www.univ-amu.fr/>
# * Centre National de la Recherche Scientifique <http://www.cnrs.fr/>
# * Université de Toulon <http://www.univ-tln.fr/>
#
# Contributors
# ------------
#
# * Ronan Hamon <firstname.lastname_AT_lis-lab.fr>
# * Valentin Emiya <firstname.lastname_AT_lis-lab.fr>
# * Florent Jaillet <firstname.lastname_AT_lis-lab.fr>
#
# Description
# -----------
#
# Python package for audio data structures with missing entries
#
# Licence
# -------
# This file is part of madarrays.
#
# madarrays is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ######### COPYRIGHT #########
"""Test of the module :mod:`mad_array`.

NOTE: This module uses random generation for some tests, the use of
pytest-randomly is recommanded to manage the seeds used in these tests.

.. moduleauthor:: Ronan Hamon
.. moduleauthor:: Valentin Emiya
"""
import tempfile
import pytest
import pickle

import numpy as np

from madarrays.mad_array import MadArray
from madarrays.mad_array import _merge_masks

from .utils import generate_mask_50


@pytest.fixture(scope='class')
def get_data(request):
    # Dimension and shape of data
    n_dims = np.random.randint(1, 3)
    request.cls.shape = 2 * np.random.randint(20, 50, n_dims)

    # For each dtype, generate two sets of data
    request.cls.x_float = np.random.random(request.cls.shape)
    request.cls.x_int = (np.random.random(
        request.cls.shape) * 2**20).astype(np.int) + 1
    request.cls.x_complex = np.random.random(
        request.cls.shape) + 1j * np.random.random(request.cls.shape)

    request.cls.x2_float = np.random.random(request.cls.shape)
    request.cls.x2_int = (np.random.random(
        request.cls.shape) * 2**20).astype(np.int) + 1
    request.cls.x2_complex = np.random.random(
        request.cls.shape) + 1j * np.random.random(request.cls.shape)

    # Generate two sets of tree masks with 50% of missing data
    request.cls.m = generate_mask_50(request.cls.shape)
    request.cls.mp = generate_mask_50(request.cls.shape)
    request.cls.mm = generate_mask_50(request.cls.shape)

    request.cls.m2 = generate_mask_50(request.cls.shape)
    request.cls.mp2 = generate_mask_50(request.cls.shape)
    request.cls.mm2 = generate_mask_50(request.cls.shape)

    # List of indices for the indexation
    request.cls.indexes = [slice(item, np.random.randint(item + 1, dim_size))
                           for dim_size in request.cls.shape
                           for item in [np.random.randint(0, dim_size - 1)]]

    request.cls.empty_mask = np.zeros(request.cls.shape, dtype=np.bool)
    request.cls.full_mask = np.ones(request.cls.shape, dtype=np.bool)


@pytest.mark.usefixtures('get_data')
class TestMadArray:

    def test_init_unmasked(self):

        for x in [self.x_float, self.x_int, self.x_complex]:
            ma = MadArray(x)

            np.testing.assert_equal(ma.to_np_array(), x)
            assert ma.dtype == x.dtype
            assert not ma._complex_masking
            assert not ma._masked_indexing
            np.testing.assert_equal(ma.unknown_mask, self.empty_mask)
            np.testing.assert_equal(ma.known_mask, self.full_mask)
            assert ma.ratio_missing_data == 0.0
            assert ma.n_missing_data == 0
            assert not ma.is_masked()

            match = 'Method not defined if masking is not complex'
            with pytest.raises(ValueError, match=match):
                ma.any_unknown_mask
            with pytest.raises(ValueError, match=match):
                ma.all_unknown_mask
            with pytest.raises(ValueError, match=match):
                ma.known_phase_mask
            with pytest.raises(ValueError, match=match):
                ma.unknown_phase_mask
            with pytest.raises(ValueError, match=match):
                ma.known_magnitude_mask
            with pytest.raises(ValueError, match=match):
                ma.unknown_magnitude_mask
            with pytest.raises(ValueError, match=match):
                ma.unknown_phase_only_mask
            with pytest.raises(ValueError, match=match):
                ma.unknown_magnitude_only_mask

    def test_init_unmasked_complex_masking(self):

        for x in [self.x_float, self.x_int, self.x_complex]:
            ma = MadArray(x, complex_masking=True)

            np.testing.assert_equal(ma.to_np_array(), x)
            assert ma.dtype == np.complex
            assert ma._complex_masking
            assert not ma._masked_indexing
            np.testing.assert_equal(ma.unknown_mask, self.empty_mask)
            np.testing.assert_equal(ma.known_mask, self.full_mask)
            np.testing.assert_equal(ma.all_unknown_mask, self.empty_mask)
            np.testing.assert_equal(ma.known_phase_mask, self.full_mask)
            np.testing.assert_equal(ma.unknown_phase_mask, self.empty_mask)
            np.testing.assert_equal(ma.known_magnitude_mask, self.full_mask)
            np.testing.assert_equal(ma.unknown_magnitude_mask, self.empty_mask)
            np.testing.assert_equal(
                ma.unknown_phase_only_mask, self.empty_mask)
            np.testing.assert_equal(
                ma.unknown_magnitude_only_mask, self.empty_mask)
            assert ma.ratio_missing_data, (0.0, 0.0)
            assert ma.n_missing_data, (0, 0)
            assert not ma.is_masked()

    def test_init_masked(self):

        for x in [self.x_float, self.x_int, self.x_complex]:
            ma = MadArray(x, mask=self.m, complex_masking=False)

            assert ma.dtype == x.dtype
            assert not ma._complex_masking
            assert not ma._masked_indexing
            assert ma.is_masked()
            np.testing.assert_equal(ma.to_np_array(), x)
            np.testing.assert_equal(ma.unknown_mask, self.m)
            np.testing.assert_equal(ma.known_mask, ~self.m)
            assert ma.ratio_missing_data, 0.5
            assert ma.n_missing_data, x.size//2
            assert ma.is_masked()
            assert not id(ma._mask) == id(self.m)

            match = 'Method not defined if masking is not complex'
            with pytest.raises(ValueError, match=match):
                ma.any_unknown_mask
            with pytest.raises(ValueError, match=match):
                ma.all_unknown_mask
            with pytest.raises(ValueError, match=match):
                ma.known_phase_mask
            with pytest.raises(ValueError, match=match):
                ma.unknown_phase_mask
            with pytest.raises(ValueError, match=match):
                ma.known_magnitude_mask
            with pytest.raises(ValueError, match=match):
                ma.unknown_magnitude_mask
            with pytest.raises(ValueError, match=match):
                ma.unknown_phase_only_mask
            with pytest.raises(ValueError, match=match):
                ma.unknown_magnitude_only_mask

        bad_shape = [item + np.random.randint(1, 100) for item in self.shape]

        match = 'Mask shape \(\d+,( \d+)?\) and data shape \(\d+,( \d+)?\) '\
                'not compatible.'
        with pytest.raises(ValueError, match=match):
            MadArray(self.x_float, np.random.random(bad_shape) < 0.3)

        with pytest.warns(UserWarning,
                          match='Argument `mask_phase` is ignored.'):
            MadArray(x, mask=self.m, mask_phase=self.mp)

        with pytest.warns(UserWarning,
                          match='Argument `mask_magnitude` is ignored.'):
            MadArray(x, mask=self.m, mask_magnitude=self.mm)

    def test_init_masked_complex_masking(self):

        for x in [self.x_float, self.x_int, self.x_complex]:

            # With phase and magnitude masks
            ma = MadArray(x, mask_phase=self.mp, mask_magnitude=self.mm,
                          complex_masking=True)

            assert ma.dtype == np.complex
            assert ma._complex_masking
            assert not ma._masked_indexing
            assert ma.is_masked()
            np.testing.assert_equal(ma.to_np_array(), x)

            np.testing.assert_equal(ma.known_mask,
                                    np.logical_and(~self.mm, ~self.mp))
            np.testing.assert_equal(ma.unknown_mask,
                                    np.logical_or(self.mm, self.mp))
            np.testing.assert_equal(ma.any_unknown_mask,
                                    np.logical_or(self.mm, self.mp))
            np.testing.assert_equal(ma.all_unknown_mask,
                                    np.logical_and(self.mm, self.mp))
            np.testing.assert_equal(ma.known_phase_mask, ~self.mp)
            np.testing.assert_equal(ma.unknown_phase_mask, self.mp)
            np.testing.assert_equal(ma.known_magnitude_mask, ~self.mm)
            np.testing.assert_equal(ma.unknown_magnitude_mask, self.mm)
            np.testing.assert_equal(ma.unknown_phase_only_mask,
                                    np.logical_and(self.mp, ~self.mm))
            np.testing.assert_equal(ma.unknown_magnitude_only_mask,
                                    np.logical_and(~self.mp, self.mm))
            assert ma.ratio_missing_data == (0.5, 0.5)
            assert ma.n_missing_data == (x.size//2, x.size//2)

            # With magnitude mask only
            ma = MadArray(x, mask_magnitude=self.mm, complex_masking=True)

            assert ma.dtype == np.complex
            assert ma._complex_masking
            assert not ma._masked_indexing
            assert ma.is_masked()
            np.testing.assert_equal(ma.to_np_array(), x)

            np.testing.assert_equal(ma.known_mask, ~self.mm)
            np.testing.assert_equal(ma.unknown_mask, self.mm)
            np.testing.assert_equal(ma.any_unknown_mask, self.mm)
            np.testing.assert_equal(ma.all_unknown_mask,
                                    np.zeros(self.shape, dtype=np.bool))
            np.testing.assert_equal(ma.known_phase_mask,
                                    np.ones(self.shape, dtype=np.bool))
            np.testing.assert_equal(ma.unknown_phase_mask,
                                    np.zeros(self.shape, dtype=np.bool))
            np.testing.assert_equal(ma.known_magnitude_mask, ~self.mm)
            np.testing.assert_equal(ma.unknown_magnitude_mask, self.mm)
            np.testing.assert_equal(ma.unknown_phase_only_mask,
                                    np.zeros(self.shape, dtype=np.bool))
            np.testing.assert_equal(ma.unknown_magnitude_only_mask, self.mm)
            assert ma.ratio_missing_data == (0.5, 0)
            assert ma.n_missing_data == (x.size//2, 0)

            # With mask_phase only
            ma = MadArray(x, mask_phase=self.mp, complex_masking=True)

            assert ma.dtype == np.complex
            assert ma._complex_masking
            assert not ma._masked_indexing
            assert ma.is_masked()
            np.testing.assert_equal(ma.to_np_array(), x)

            np.testing.assert_equal(ma.known_mask, ~self.mp)
            np.testing.assert_equal(ma.unknown_mask, self.mp)
            np.testing.assert_equal(ma.any_unknown_mask, self.mp)
            np.testing.assert_equal(ma.all_unknown_mask,
                                    np.zeros(self.shape, dtype=np.bool))
            np.testing.assert_equal(ma.known_phase_mask, ~self.mp)
            np.testing.assert_equal(ma.unknown_phase_mask, self.mp)
            np.testing.assert_equal(ma.known_magnitude_mask,
                                    np.ones(self.shape, dtype=np.bool))
            np.testing.assert_equal(ma.unknown_magnitude_mask,
                                    np.zeros(self.shape, dtype=np.bool))
            np.testing.assert_equal(ma.unknown_phase_only_mask, self.mp)
            np.testing.assert_equal(ma.unknown_magnitude_only_mask,
                                    np.zeros(self.shape, dtype=np.bool))
            assert ma.ratio_missing_data == (0, 0.5)
            assert ma.n_missing_data == (0, x.size//2)

        bad_shape = [item + np.random.randint(1, 100) for item in self.shape]

        match = 'Phase mask shape \(\d+,( \d+)?\) and data shape '\
                '\(\d+,( \d+)?\) not compatible.'
        with pytest.raises(ValueError, match=match):
            MadArray(self.x_complex, complex_masking=True,
                     mask_phase=np.random.random(bad_shape) < 0.8)

        match = 'Magnitude mask shape \(\d+,( \d+)?\) and data shape '\
                '\(\d+,( \d+)?\) not compatible.'
        with pytest.raises(ValueError, match=match):
            MadArray(self.x_complex, complex_masking=True,
                     mask_magnitude=np.random.random(bad_shape) < 0.8)

        with pytest.warns(UserWarning, match='Argument `mask` is ignored.'):
            MadArray(self.x_complex, mask=self.m, mask_phase=self.mp,
                     complex_masking=True)

    def test_init_maskedarray(self):

        for x in [self.x_float, self.x_int, self.x_complex]:

            old_ma = MadArray(x, self.m)
            ma = MadArray(old_ma)

            np.testing.assert_equal(ma.unknown_mask, self.m)
            assert id(old_ma) != id(ma)
            assert id(old_ma._mask) != id(ma._mask)

            old_ma = MadArray(x, self.m)
            ma = MadArray(old_ma, mask=self.mp)

            np.testing.assert_equal(ma.unknown_mask, self.mp)
            assert id(old_ma) != id(ma)
            assert id(old_ma._mask) != id(ma._mask)

    def test_init_maskedarray_complexmasking(self):

        for x in [self.x_float, self.x_int, self.x_complex]:
            old_ma = MadArray(x, mask_phase=self.mp,
                              mask_magnitude=self.mm, complex_masking=True)
            ma = MadArray(old_ma)

            assert id(old_ma) != id(ma)
            assert id(old_ma._mask) != id(ma._mask)

            old_ma = MadArray(x, mask_phase=self.mp,
                              mask_magnitude=self.mm, complex_masking=True)
            ma = MadArray(old_ma, mask_phase=self.mm,
                          mask_magnitude=self.mp)

            np.testing.assert_equal(ma.unknown_phase_mask, self.mm)
            np.testing.assert_equal(ma.unknown_magnitude_mask, self.mp)
            assert id(old_ma) != id(ma)
            assert id(old_ma._mask) != id(ma._mask)

        for x in [self.x_float, self.x_int, self.x_complex]:
            old_ma = MadArray(x, mask_phase=self.mp,
                              mask_magnitude=self.mm, complex_masking=True)

            old_ma = MadArray(x, mask=self.m, complex_masking=False)
            ma = MadArray(old_ma, complex_masking=True)

            assert id(old_ma) != id(ma)
            assert id(old_ma._mask) != id(ma._mask)
            assert ma._complex_masking

            old_ma = MadArray(x, mask_phase=self.mp,
                              mask_magnitude=self.mm, complex_masking=True)
            ma = MadArray(old_ma, mask_phase=self.mm,
                          mask_magnitude=self.mp)

            np.testing.assert_equal(ma.unknown_phase_mask, self.mm)
            np.testing.assert_equal(ma.unknown_magnitude_mask, self.mp)
            assert id(old_ma) != id(ma)
            assert id(old_ma._mask) != id(ma._mask)

    def test_init_other_dtype(self):

        # From list
        ma = MadArray(self.x_float.tolist())

        np.testing.assert_equal(ma.to_np_array(), self.x_float)
        assert np.issubdtype(ma.dtype, np.floating)

        # Raises
        x = np.array([[1, 'b'], [2, 2], [2, 4]])
        with pytest.raises(TypeError, match='Invalid dtype: <U21'):
            MadArray(x)

    def test_masked_indexing(self):

        ma = MadArray(self.x_float, self.m)
        ma_slice = ma[self.indexes]

        assert isinstance(ma_slice, MadArray)
        np.testing.assert_equal(ma_slice, self.x_float[self.indexes])
        np.testing.assert_equal(ma_slice.unknown_mask, self.m[self.indexes])
        np.testing.assert_equal(ma_slice.known_mask, ~self.m[self.indexes])
        assert ma_slice.ratio_missing_data == np.mean(self.m[self.indexes])
        assert ma_slice.n_missing_data == np.sum(self.m[self.indexes])
        assert ma.is_masked()

    def test_masked_indexing_masked(self):

        ma = MadArray(self.x_float, mask=self.m, masked_indexing=True)
        m_index = np.zeros(self.shape, dtype=np.bool)
        m_index[self.indexes] = 1

        ma_slice = ma[self.indexes]

        assert isinstance(ma_slice, MadArray)
        np.testing.assert_equal(ma_slice.shape, self.shape)
        np.testing.assert_equal(ma_slice, self.x_float)
        np.testing.assert_equal(ma_slice.unknown_mask,
                                np.logical_or(~m_index, self.m))
        np.testing.assert_equal(ma_slice.known_mask,
                                np.logical_and(m_index, ~self.m))
        assert (ma_slice.ratio_missing_data == np.mean(
            np.logical_or(~m_index, self.m)))
        assert ma_slice.n_missing_data == np.sum(
            np.logical_or(~m_index, self.m))
        assert ma.is_masked()

    def test_to_np_array(self):
        ma = MadArray(self.x_float, self.m)

        az = ma.to_np_array(fill_value=24)
        assert type(az) == np.ndarray
        np.testing.assert_equal(az[self.m], 24)
        np.testing.assert_equal(az[~self.m], self.x_float[~self.m])

        ma = MadArray(self.x_float, mask_phase=self.mp,
                      mask_magnitude=self.mm, complex_masking=True)

        xma = ma.to_np_array(0)

        np.testing.assert_almost_equal(
            xma[ma.unknown_phase_only_mask],
            np.abs(self.x_float[ma.unknown_phase_only_mask]) + 0 * 1j)
        np.testing.assert_almost_equal(
            xma[ma.unknown_magnitude_only_mask],
            np.exp(
                1j * np.angle(self.x_float[ma.unknown_magnitude_only_mask])))
        np.testing.assert_equal(xma[ma.all_unknown_mask], 0 + 0j)

        ma = MadArray(self.x_float, self.m)
        xma = ma.to_np_array()
        np.testing.assert_equal(xma, self.x_float)

    def test_copy(self):

        ma = MadArray(self.x_float, self.m)

        ma_copy = ma.copy()
        assert ma.is_equal(ma_copy)
        assert id(ma) != id(ma_copy)
        assert id(ma._mask) != id(ma_copy._mask)

    def test_basic_operations(self):
        match = 'Operation not permitted when complex masking.'
        for operator in ['+', '-', '*', '/', '//']:
            print('Operation: {}'.format(operator))

            for x in [self.x_float, self.x_int, self.x_complex]:

                ma = MadArray(x, self.m)

                for x2 in [self.x2_float, self.x2_int, self.x2_complex]:
                    xs = eval('x {} x2'.format(operator))
                    ms = eval('ma {} x2'.format(operator))

                    assert isinstance(ms, MadArray)
                    assert not ms._complex_masking
                    assert ms.dtype == xs.dtype
                    np.testing.assert_equal(ms, xs)
                    np.testing.assert_equal(ms._mask, self.m)

                    ma2 = MadArray(x2, self.m2)
                    ms = eval('ma {} ma2'.format(operator))

                    assert isinstance(ms, MadArray)
                    assert not ms._complex_masking
                    assert ms.dtype == xs.dtype
                    np.testing.assert_equal(ms, xs)
                    np.testing.assert_equal(ms._mask,
                                            np.logical_or(self.m, self.m2))

                for x2 in [self.x2_float, self.x2_int, self.x2_complex]:

                    ma2 = MadArray(x2, mask_phase=self.mp2,
                                   mask_magnitude=self.mm2,
                                   complex_masking=True)

                    with pytest.raises(ValueError, match=match):
                        eval('ma {} ma2'.format(operator))

            for x in [self.x_float, self.x_int, self.x_complex]:
                ma = MadArray(x, mask_phase=self.mp,
                              mask_magnitude=self.mm, complex_masking=True)

                for x2 in [self.x2_float, self.x2_int, self.x2_complex]:
                    ma2 = MadArray(x2, self.m2)
                    with pytest.raises(ValueError, match=match):
                        eval('ma {} ma2'.format(operator))

                for x2 in [self.x2_float, self.x2_int, self.x2_complex]:
                    ma2 = MadArray(x2, mask_phase=self.mp2,
                                   mask_magnitude=self.mm2,
                                   complex_masking=True)

                    with pytest.raises(ValueError, match=match):
                        ma + ma2

    def test_advanced_operations(self):

        for x in [self.x_float, self.x_int, self.x_complex]:

            ma = MadArray(x, self.m)

            m = np.mean(ma)
            assert not isinstance(m, MadArray)
            np.testing.assert_equal(m, np.mean(x))

            m = np.mean(ma, axis=0)
            assert not isinstance(m, MadArray)
            np.testing.assert_equal(m, np.mean(x, axis=0))

            m = np.std(ma)
            assert not isinstance(m, MadArray)
            np.testing.assert_equal(m, np.std(x))

            m = np.abs(ma)
            assert isinstance(m, MadArray)
            np.testing.assert_equal(m, np.abs(x))

            m = np.sqrt(ma)
            assert isinstance(m, MadArray)
            np.testing.assert_equal(m, np.sqrt(x))

            m = ma**2
            assert isinstance(m, MadArray)
            np.testing.assert_equal(m, x**2)

            m = np.conj(ma)
            assert isinstance(m, MadArray)
            np.testing.assert_equal(m, np.conj(x))

            if np.issubdtype(ma.dtype, np.floating):
                m = np.floor(ma)
                assert isinstance(m, MadArray)
                np.testing.assert_equal(m, np.floor(x))

                m = np.ceil(ma)
                assert isinstance(m, MadArray)
                np.testing.assert_equal(m, np.ceil(x))

            a = ma < np.mean(ma)
            assert not isinstance(a, MadArray)
            np.testing.assert_equal(a, x < np.mean(ma))

            a = ma >= np.mean(ma)
            assert not isinstance(a, MadArray)
            np.testing.assert_equal(a, x >= np.mean(ma))

    def test_eq_ne_numpy(self):

        ma = MadArray(self.x_float)
        eq = ma == self.x_float
        assert type(eq) == np.ndarray
        assert eq.dtype == np.bool
        assert np.all(eq)

        ma_neq = ma != self.x2_float
        assert type(ma_neq) == np.ndarray
        assert ma_neq.dtype == np.bool
        assert np.all(ma_neq)

        ma = MadArray(self.x_float, self.m)
        ma_eq = ma == self.x_float
        assert type(ma_eq) == np.ndarray
        assert ma_eq.dtype == np.bool
        assert np.all(ma_eq[ma.known_mask])

        neq = ma != self.x2_float
        assert type(neq) == np.ndarray
        assert neq.dtype == np.bool
        assert np.all(neq)

    def test_eq_ne_maskedarray(self):

        ma1 = MadArray(self.x_float, self.m)
        ma2 = MadArray(self.x_float, self.m)
        ma3 = MadArray(self.x2_float, self.m2)

        eq = ma1 == ma2
        assert type(eq) == np.ndarray
        assert eq.dtype == np.bool
        assert np.all(eq)

        neq = ma1 != ma3
        assert type(neq) == np.ndarray
        assert neq.dtype == np.bool
        assert np.any(neq)

    def test_is_equal(self):

        ma1 = MadArray(self.x_float, self.m)
        ma2 = MadArray(self.x_float, self.m)
        ma3 = MadArray(self.x_float, self.m2)
        ma4 = MadArray(self.x2_float, self.m)
        ma5 = MadArray(self.x_float, mask_phase=self.mp,
                       complex_masking=True)
        ma6 = MadArray(self.x_float, self.m, masked_indexing=True)

        assert ma1.is_equal(ma2)
        assert not ma1.is_equal(self.x_float)
        assert not ma1.is_equal(ma3)
        assert not ma1.is_equal(ma4)
        assert not ma1.is_equal(ma5)
        assert not ma1.is_equal(ma6)

    def test_transpose(self):

        ma_float = MadArray(self.x_float, self.m)

        tma = ma_float.T

        np.testing.assert_equal(tma.unknown_mask, self.m.T)
        np.testing.assert_equal(np.array(tma)[tma.known_mask],
                                self.x_float.T[tma.known_mask])

    def test_pickle(self):

        # float dtype
        ma = MadArray(self.x_float, self.m)

        with tempfile.NamedTemporaryFile() as tmp_file:
            with open(tmp_file.name, 'wb') as fout:
                pickle.dump(ma, fout)

            with open(tmp_file.name, 'rb') as fin:
                pma = pickle.load(fin)

            assert ma.is_equal(pma)

        # int  dtype
        ma = MadArray(self.x_int, self.m)

        with tempfile.NamedTemporaryFile() as tmp_file:
            with open(tmp_file.name, 'wb') as fout:
                pickle.dump(ma, fout)

            with open(tmp_file.name, 'rb') as fin:
                pma = pickle.load(fin)

            assert ma.is_equal(pma)

        # complex dtype
        ma = MadArray(self.x_complex, mask_phase=self.mp,
                      mask_magnitude=self.mm, complex_masking=True)

        with tempfile.NamedTemporaryFile() as tmp_file:
            with open(tmp_file.name, 'wb') as fout:
                pickle.dump(ma, fout)

            with open(tmp_file.name, 'rb') as fin:
                pma = pickle.load(fin)

            assert ma.is_equal(pma)

    def test_str_repr(self):

        # test when no data is missing
        x = np.copy(self.x_float)
        arr_str = np.ndarray.__str__(x)

        ma = MadArray(self.x_float)
        string = 'MadArray, dtype=float64, 0 missing entries (0.0%)\n{}'
        assert str(ma) == string.format(arr_str)

        # test with missing data, float values
        x[self.m] = np.nan
        arr_str = np.ndarray.__str__(x)
        arr_str = arr_str.replace('nan', '  x')

        ma = MadArray(self.x_float, self.m)
        n_miss = np.count_nonzero(self.m)
        string = 'MadArray, dtype=float64, {} missing entries (50.0%)\n{}'
        assert str(ma) == string.format(n_miss, arr_str)

        string = '<MadArray at {}>'
        assert repr(ma) == string.format(hex(id(ma)))

        # test with missing data, float values from int
        x = np.copy(self.x_int).astype(np.float64)
        x[self.m] = np.nan
        arr_str = np.ndarray.__str__(x)
        arr_str = arr_str.replace('nan', '  x')
        arr_str = arr_str.replace('.', '')

        ma = MadArray(self.x_int, self.m)
        n_miss = np.count_nonzero(self.m)
        string = 'MadArray, dtype=int64, {} missing entries (50.0%)\n{}'
        assert str(ma) == string.format(n_miss, arr_str)

        string = '<MadArray at {}>'
        assert repr(ma) == string.format(hex(id(ma)))

        # test with missing data, complex values, binary mask
        x = np.copy(self.x_complex)
        x[self.m] = np.nan
        arr_str = np.ndarray.__str__(x)
        arr_str = arr_str.replace('nan+0.j', '  x    ')

        ma = MadArray(self.x_complex, self.m)
        n_miss = np.count_nonzero(self.m)
        string = 'MadArray, dtype=complex128, {} missing entries (50.0%)\n{}'
        assert str(ma) == string.format(n_miss, arr_str)

        string = '<MadArray at {}>'
        assert repr(ma) == string.format(hex(id(ma)))

        # test with missing data, complex values, complex_masking
        x = np.copy(self.x_complex)
        m_any = np.logical_or(self.mm, self.mp)
        x[m_any] = np.nan
        arr_str = np.ndarray.__str__(x)
        arr_str = arr_str.replace('nan+0.j', '  x    ')

        ma = MadArray(self.x_complex, complex_masking=True,
                      mask_magnitude=self.mm, mask_phase=self.mp)
        m_all = np.logical_and(self.mm, self.mp)
        n_miss = np.count_nonzero(m_all)
        n_miss_m = np.count_nonzero(self.mm)
        n_miss_p = np.count_nonzero(self.mp)
        string = \
            'MadArray, dtype=complex128, ' \
            '{} missing magnitudes ({:.1%}) ' \
            'and {} missing phases ({:.1%}),  ' \
            'including {} missing magnitudes and phases jointly ({:.1%})' \
            '\n{}'
        assert str(ma) == string.format(n_miss_m, n_miss_m / x.size,
                                        n_miss_p, n_miss_p / x.size,
                                        n_miss, n_miss / x.size,
                                        arr_str)

        string = '<MadArray at {}>'
        assert repr(ma) == string.format(hex(id(ma)))

    def test_merge_masks(self):
        ma1 = MadArray(self.x_float, self.m)
        ma2 = MadArray(self.x_float, self.m2)

        output = _merge_masks(ma1, ma2)

        assert isinstance(output, dict)
        assert 'mask' in output
        np.testing.assert_equal(output['mask'], np.logical_or(self.m, self.m2))

        ma1 = MadArray(self.x_float, self.m)
        ma2 = MadArray(self.x_complex, mask_magnitude=self.mm,
                       mask_phase=self.mp, complex_masking=True)

        output = _merge_masks(ma1, ma2)

        assert isinstance(output, dict)
        assert 'mask_magnitude' in output
        assert 'mask_phase' in output
        np.testing.assert_equal(output['mask_magnitude'],
                                np.logical_or(self.m, self.mm))

        np.testing.assert_equal(output['mask_phase'],
                                np.logical_or(self.m, self.mp))

        output = _merge_masks(ma2, ma1)

        assert isinstance(output, dict)
        assert 'mask_magnitude' in output
        assert 'mask_phase' in output
        np.testing.assert_equal(output['mask_magnitude'],
                                np.logical_or(self.m, self.mm))

        np.testing.assert_equal(output['mask_phase'],
                                np.logical_or(self.m, self.mp))
