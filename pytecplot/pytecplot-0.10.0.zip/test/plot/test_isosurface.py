import os
import unittest

import tecplot as tp
from tecplot.constant import *
from tecplot.exception import *
from tecplot.plot.isosurface import (
    IsosurfaceContour,
    IsosurfaceEffects,
    IsosurfaceGroup,
    IsosurfaceMesh,
    IsosurfaceShade)

from ..sample_data import sample_data
from tecplot.tecutil import Index
from ..property_test import PropertyTest
from ..plot import ContourGroup

from test import skip_on, skip_if_sdk_version_before, mocked_sdk_version


class TestIsosurface(PropertyTest):
    def setUp(self):
        tp.new_layout()
        self.filename, self.dataset = sample_data('2x2x3_overlap')
        frame = tp.active_frame()
        self.frame = frame

        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        self.iso = self.plot.isosurface(0)  # type: IsosurfaceGroup

    def tearDown(self):
        os.remove(self.filename)

    def _check_iso_values(self, v1, v2=None, v3=None):
        self.assertEqual(v1, self.iso.isosurface_values[0])
        if v2 is not None:
            self.assertEqual(v2, self.iso.isosurface_values[1])
        if v3 is not None:
            self.assertEqual(v3, self.iso.isosurface_values[2])

    def test_iso_values_len(self):
        self.assertEqual(3, len(self.iso.isosurface_values))

    def test_iso_values_str(self):
        self.iso.isosurface_values = (0, 0, 0)
        self.assertEqual('(0.0, 0.0, 0.0)', str(self.iso.isosurface_values))

    def test_iso_values_repr(self):
        self.iso.isosurface_values = (0, 0, 0)
        self.assertEqual('(0.0, 0.0, 0.0)', repr(self.iso.isosurface_values))

    def test_iso_bad_index(self):
        with self.assertRaises(IndexError):
            self.iso.isosurface_values[10] = .7

        with self.assertRaises(IndexError):
            self.iso.isosurface_values[-4] = .8

        with self.assertRaises(TypeError):
            self.iso.isosurface_values['abc'] = 0

    def test_iso_values_scalar(self):
        original_values = tuple(self.iso.isosurface_values)
        self.iso.isosurface_values = 0.5
        self.assertEqual(self.iso.isosurface_values[0], 0.5)
        self.assertEqual(tuple(self.iso.isosurface_values),
                         (0.5, original_values[1], original_values[2]))
        self._check_iso_values(0.5)

    def test_iso_values_scalar_error(self):
        with self.assertRaises((ValueError, TypeError)):
            self.iso.isosurface_values = 'abc'
        with self.assertRaises(TypeError):
            self.iso.isosurface_values = None

    def test_iso_values_error(self):
        with self.assertRaises(TypeError):
            self.iso.isosurface_values = (None, None, None)

    def test_iso_1_tuple(self):
        self.iso.isosurface_values = (.5,)
        self._check_iso_values(.5)

    def test_iso_2_tuple(self):
        self.iso.isosurface_values = (.1, .2)
        self._check_iso_values(.1, .2)

    def test_iso_3_tuple(self):
        self.iso.isosurface_values = (.1, .2, .3)
        self._check_iso_values(.1, .2, .3)

    def test_group(self):
        self.assertIsInstance(self.plot.isosurface(0), IsosurfaceGroup)

    def test_contour(self):
        self.assertIsInstance(self.iso.contour, IsosurfaceContour)
        with self.assertRaises(AttributeError):
            self.iso.contour = None

    def test_effects(self):
        self.assertIsInstance(self.iso.effects, IsosurfaceEffects)
        with self.assertRaises(AttributeError):
            self.iso.effects = None

    def test_mesh(self):
        self.assertIsInstance(self.iso.mesh, IsosurfaceMesh)
        with self.assertRaises(AttributeError):
            self.iso.mesh = None

    def test_shade(self):
        self.assertIsInstance(self.iso.shade, IsosurfaceShade)
        with self.assertRaises(AttributeError):
            self.iso.shade = None

    def test_eq(self):
        iso_0 = self.plot.isosurface(0)
        self.assertTrue(iso_0 == self.plot.isosurface(0))
        self.assertTrue(iso_0 != self.plot.isosurface(1))
        self.assertFalse(iso_0 == self.plot.isosurface(1))
        self.assertFalse(iso_0 != self.plot.isosurface(0))

    def test_group_round_trip(self):
        for api, value in (
                ('show', bool),
                ('isosurface_selection', IsoSurfaceSelection),
                ('definition_contour_group_index', Index),
                ('definition_contour_group', ContourGroup(1, self.plot)),
                ('obey_source_zone_blanking', bool),
        ):
            self.internal_test_property_round_trip(
                api, value, IsosurfaceGroup, self.iso)

    def test_group_values(self):
        for i in range(3):
            for val in [-1., 0., 0.5]:
                self.iso.isosurface_values[i] = val
                self.assertAlmostEqual(self.iso.isosurface_values[i], val)
            with self.assertRaises(ValueError):
                self.iso.isosurface_values[i] = 'badtype'

    @skip_if_sdk_version_before(2017, 2)
    @skip_on(TecplotOutOfDateEngineError)
    def test_surface_generation_method(self):
        if __debug__:
            with mocked_sdk_version(2017, 2):
                with self.assertRaises(TecplotOutOfDateEngineError):
                    self.iso.surface_generation_method = \
                        SurfaceGenerationMethod.AllPolygons

                for val in [SurfaceGenerationMethod.AllowQuads,
                            SurfaceGenerationMethod.AllTriangles]:
                    self.iso.surface_generation_method = val
                    self.assertEqual(self.iso.surface_generation_method, val)
        elif tp.sdk_version_info < (2018, 1):
            raise unittest.SkipTest('Changed in SDK in 2018.1')

        for val in SurfaceGenerationMethod:
            self.iso.surface_generation_method = val
            self.assertEqual(self.iso.surface_generation_method, val)

    def test_contour_round_trip(self):
        for api, value in (
                ('show', bool),
                ('contour_type', ContourType),
                ('flood_contour_group_index', Index),
                ('flood_contour_group', ContourGroup(1, self.plot)),
                ('line_contour_group_index', Index),
                ('line_contour_group', ContourGroup(1, self.plot)),
                ('line_color', Color),
                ('line_thickness', float)
        ):
            self.internal_test_property_round_trip(
                api, value, IsosurfaceContour, self.iso.contour)

    def test_mesh_round_trip(self):
        for api, value in (
                ('show', bool),
                ('color', Color),
                ('line_thickness', float)
        ):
            self.internal_test_property_round_trip(
                api, value, IsosurfaceMesh, self.iso.mesh)

    def test_effects_round_trip(self):
        for api, value in (
                ('lighting_effect', LightingEffect),
                ('surface_translucency', 1),
                ('surface_translucency', 99),
                ('use_translucency', bool)
        ):
            self.internal_test_property_round_trip(
                api, value, IsosurfaceEffects, self.iso.effects)

    def test_shade_round_trip(self):
        for api, value in (
                ('show', bool),
                ('color', Color),
        ):
            self.internal_test_property_round_trip(
                api, value, IsosurfaceShade, self.iso.shade)


class TestIsosurfaceContour(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename, self.dataset = sample_data('2x2x3_overlap')
        frame = tp.active_frame()
        self.frame = frame

        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        self.iso = self.plot.isosurface(0)

    def tearDown(self):
        os.remove(self.filename)

    @skip_if_sdk_version_before(2017, 3)
    def test_use_lighting_effect(self):
        self.iso.shade.use_lighting_effect = False
        for val in [True, False, True]:
            self.iso.contour.use_lighting_effect = val
            self.assertEqual(self.iso.contour.use_lighting_effect, val)
            self.assertEqual(self.iso.shade.use_lighting_effect, False)


class TestIsosurfaceShade(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename, self.dataset = sample_data('2x2x3_overlap')
        frame = tp.active_frame()
        self.frame = frame

        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        self.iso = self.plot.isosurface(0)

    def tearDown(self):
        os.remove(self.filename)

    @skip_if_sdk_version_before(2017, 3)
    def test_use_lighting_effect(self):
        self.iso.contour.use_lighting_effect = False
        for val in [True, False, True]:
            self.iso.shade.use_lighting_effect = val
            self.assertEqual(self.iso.shade.use_lighting_effect, val)
            self.assertEqual(self.iso.contour.use_lighting_effect, False)

class TestIsosurfaceVector(unittest.TestCase):
    @skip_if_sdk_version_before(2017, 3)
    def setUp(self):
        tp.new_layout()
        self.datafile, ds = sample_data('3x3x3_p')
        frame = tp.active_frame()
        frame.plot_type = PlotType.Cartesian3D
        plot = frame.plot(PlotType.Cartesian3D)
        plot.vector.u_variable = ds.variable(0)
        plot.vector.v_variable = ds.variable(1)
        plot.vector.w_variable = ds.variable(2)
        self.isovec = plot.isosurface(0).vector

    def tearDown(self):
        os.remove(self.datafile)

    def test_show(self):
        for val in [True, False, True]:
            self.isovec.show = val
            self.assertEqual(self.isovec.show, val)

    def test_vector_type(self):
        for val in [VectorType.TailAtPoint, VectorType.HeadAtPoint,
                    VectorType.MidAtPoint]:
            self.isovec.vector_type = val
            self.assertEqual(self.isovec.vector_type, val)
        with self.assertRaises(ValueError):
            self.isovec.vector_type = 0.5

    def test_arrowhead_style(self):
        for val in [ArrowheadStyle.Plain, ArrowheadStyle.Filled,
                    ArrowheadStyle.Hollow]:
            self.isovec.arrowhead_style = val
            self.assertEqual(self.isovec.arrowhead_style, val)
        with self.assertRaises(ValueError):
            self.isovec.arrowhead_style = 0.5

    def test_color(self):
        for val in [Color.Black, Color.Red, Color.Blue,
                    self.isovec.isosurface.plot.contour(0)]:
            self.isovec.color = val
            self.assertEqual(self.isovec.color, val)
        with self.assertRaises(ValueError):
            self.isovec.color = 0.5

    def test_is_tangent(self):
        for val in [True, False, True]:
            self.isovec.is_tangent = val
            self.assertEqual(self.isovec.is_tangent, val)

    def test_line_thickness(self):
        for val in [0.5, 1, 2, 100]:
            self.isovec.line_thickness = val
            self.assertEqual(self.isovec.line_thickness, val)
        with self.assertRaises(ValueError):
            self.isovec.line_thickness = 'badtype'
        with self.assertRaises(TecplotSystemError):
            self.isovec.line_thickness = -1
        with self.assertRaises(TecplotSystemError):
            self.isovec.line_thickness = 0
        with self.assertRaises(TecplotSystemError):
            self.isovec.line_thickness = 101


if __name__ == '__main__':
    from .. import main
    main()
