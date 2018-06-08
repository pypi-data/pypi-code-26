from __future__ import unicode_literals

import base64
import numpy as np
import os
import unittest
import zlib

from tempfile import NamedTemporaryFile

import tecplot as tp
from tecplot.tecutil import _tecutil, sv, IndexSet
from tecplot.constant import *
from tecplot.exception import *
from .. import patch_tecutil
from tecplot.tecutil import ArgList

from test import patch_tecutil, skip_if_sdk_version_before
from ..sample_data import *


class TestProbeAtPosition(unittest.TestCase):
    def setUp(self):
        self.filenames = {
            '3x3x3_p' : sample_data_file('3x3x3_p'),
            '3x3x1_p' : sample_data_file('3x3x1_p'),
            '3x1x3_p' : sample_data_file('3x1x3_p'),
            '1x3x3_p' : sample_data_file('1x3x3_p'),
            '2x2x3_overlap' :sample_data_file('2x2x3_overlap')}

    def tearDown(self):
        for f in self.filenames.values():
            os.remove(f)

    def test_probe_3d(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['3x3x3_p'])
        fr = tp.active_frame()
        fr.plot_type = PlotType.Cartesian3D
        data,cell,zone = tp.data.query.probe_at_position(.1,.3,.5)
        self.assertTrue(np.allclose(data, [.1,.3,.5,.125]))
        self.assertTrue(np.allclose(cell,[0,0,0]))
        self.assertEqual(zone, ds.zone(0))
        self.assertEqual(data[0], 0.1)
        self.assertEqual(data[1], 0.3)
        self.assertEqual(data[2], 0.5)
        self.assertEqual(data[3], 0.125)

        self.assertEqual(data[3], data[ds.variable('P').index])
        self.assertEqual(data[3], data[list(ds.variables('P'))[0].index])

        res = tp.data.query.probe_at_position(.1,.35,.5,starting_cell=cell,
                                        starting_zone=zone)
        data,cell,zone = res
        self.assertTrue(np.allclose(data, [.1,.35,.5,.15]))
        self.assertTrue(np.allclose(cell,[0,0,0]))
        self.assertEqual(zone, ds.zone(0))
        self.assertEqual(data[0], 0.1)
        self.assertEqual(data[1], 0.35)
        self.assertEqual(data[2], 0.5)
        self.assertEqual(data[3], 0.15)

    def test_probe_overlapping_zones(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])
        zone1,zone2 = ds.zones()

        # probe_at_position in zone1 only region
        res = tp.data.query.probe_at_position(.1,.3,.5)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 0.5, 0.35]))
        self.assertEqual(res.cell, (0,0,0))
        self.assertEqual(res.zone, zone1)

        res = tp.data.query.probe_at_position(.1,.3,.5,
            starting_cell=res.cell,starting_zone=res.zone)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 0.5, 0.35]))
        self.assertEqual(res.cell, (0,0,0))
        self.assertEqual(res.zone, zone1)

        res = tp.data.query.probe_at_position(.1,.3,.5,
            starting_cell=res.cell,starting_zone=zone2)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 0.5, 0.35]))
        self.assertEqual(res.cell, (0,0,0))
        self.assertEqual(res.zone, zone1)

        # probe_at_position in shared region
        res = tp.data.query.probe_at_position(.1,.3,1.5)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 1.5, 0.15]))
        self.assertEqual(res.cell, (0,0,1))
        self.assertEqual(res.zone, zone1)

        res = tp.data.query.probe_at_position(.1,.3,1.5,
            starting_cell=res.cell,starting_zone=res.zone)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 1.5, 0.15]))
        self.assertEqual(res.cell, (0,0,1))
        self.assertEqual(res.zone, zone1)

        res = tp.data.query.probe_at_position(.1,.3,1.5,
            starting_cell=res.cell,starting_zone=zone1)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 1.5, 0.15]))
        self.assertEqual(res.cell, (0,0,1))
        self.assertEqual(res.zone, zone1)

        res = tp.data.query.probe_at_position(.1,.3,1.5,
            starting_cell=res.cell,starting_zone=zone2)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 1.5, 0.05]))
        self.assertEqual(res.cell, (0,0,0))
        self.assertEqual(res.zone, zone2)

        # probe_at_position in zone2 only region
        res = tp.data.query.probe_at_position(.1,.3,2.5)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 2.5, 0.45]))
        self.assertEqual(res.cell, (0,0,1))
        self.assertEqual(res.zone, zone2)

        res = tp.data.query.probe_at_position(.1,.3,2.5,
            starting_cell=res.cell,starting_zone=res.zone)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 2.5, 0.45]))
        self.assertEqual(res.cell, (0,0,1))
        self.assertEqual(res.zone, zone2)

        res = tp.data.query.probe_at_position(.1,.3,2.5,
            starting_cell=res.cell,starting_zone=zone1)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 2.5, 0.45]))
        self.assertEqual(res.cell, (0,0,1))
        self.assertEqual(res.zone, zone2)

    def test_probe_3d_data_in_2d(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['3x3x3_p'])
        fr = tp.active_frame()
        fr.plot_type = PlotType.Cartesian2D
        result = tp.data.query.probe_at_position(.15,.8)
        data,cell,zone = result.data,result.cell,result.zone
        self.assertTrue(np.allclose(data, [.15,.8,0,.85]))
        self.assertTrue(np.allclose(cell,[0,1,0]))
        self.assertEqual(zone, ds.zone(0))
        self.assertEqual(data[0], 0.15)
        self.assertEqual(data[1], 0.8)
        self.assertEqual(data[2], 0.)
        self.assertEqual(data[3], 0.85)

    def test_probe_2d(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['3x3x1_p'])
        fr = tp.active_frame()
        fr.plot_type = PlotType.Cartesian2D

        data,cell,zone = tp.data.query.probe_at_position(.1,.7)
        self.assertTrue(np.allclose(data, [.1,.7,.65]))
        self.assertEqual(cell, (0,1,0))
        self.assertEqual(zone, ds.zone(0))


        ds = tp.data.load_tecplot(self.filenames['3x1x3_p'], read_data_option=ReadDataOption.ReplaceInActiveFrame)
        fr = tp.active_frame()
        fr.plot_type = PlotType.Cartesian2D
        fr.plot().axes.y_axis.variable = ds.variable('Z')

        data,cell,zone = tp.data.query.probe_at_position(.1,.7)
        self.assertTrue(np.allclose(data, [.1,0,.7,.65]))
        self.assertEqual(cell, (0,0,1))
        self.assertEqual(zone, ds.zone(0))
        self.assertEqual(data[3], data[ds.variable('P').index])


        ds = tp.data.load_tecplot(self.filenames['1x3x3_p'], read_data_option=ReadDataOption.ReplaceInActiveFrame)
        fr = tp.active_frame()
        fr.plot_type = PlotType.Cartesian2D
        fr.plot().axes.x_axis.variable = ds.variable('Y')
        fr.plot().axes.y_axis.variable = ds.variable('Z')

        data,cell,zone = tp.data.query.probe_at_position(.1,.7)
        self.assertTrue(np.allclose(data, [0,.1,.7,.65]))
        self.assertEqual(cell, (0,0,1))
        self.assertEqual(zone, ds.zone(0))
        self.assertEqual(data[3], data[ds.variable('P').index])

    def test_logic_errors(self):
        tp.new_layout()
        fr0 = tp.active_frame()
        ds0 = tp.data.load_tecplot(self.filenames['3x3x3_p'])
        fr1 = tp.active_page().add_frame()
        ds1 = tp.data.load_tecplot(self.filenames['3x3x3_p'])
        if __debug__:
            with self.assertRaises(TecplotValueError):
                tp.data.query.probe_at_position(.1,.3,.5,dataset=ds0,frame=fr1)
            with self.assertRaises((TecplotLogicError, AttributeError)):
                tp.data.query.probe_at_position(.1,.3,.5, starting_cell=(0,0,0))
        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            class A():
                index = -10
            tp.data.query.probe_at_position(.1,.3,.5,starting_cell=(0,0,0),
                                      starting_zone=A())

    def test_probe_zones(self):
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'], read_data_option=ReadDataOption.ReplaceInActiveFrame)
        fr = tp.active_frame()
        fr.plot_type = PlotType.Cartesian3D
        zone1,zone2 = ds.zones()

        res = tp.data.query.probe_at_position(.1,.3,1.5,zones=[zone1])
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 1.5, 0.15]))
        self.assertEqual(res.cell, (0,0,1))
        self.assertEqual(res.zone, zone1)

        res = tp.data.query.probe_at_position(.1,.3,1.5,zones=[zone2])
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 1.5, 0.05]))
        self.assertEqual(res.cell, (0,0,0))
        self.assertEqual(res.zone, zone2)

    def test_probe_dataset(self):
        tp.new_layout()
        fr0 = tp.active_frame()
        ds0 = tp.data.load_tecplot(self.filenames['3x3x3_p'])
        fr1 = tp.active_page().add_frame()
        ds1 = tp.data.load_tecplot(self.filenames['3x3x3_p'])

        fr1.activate()
        res_a = tp.data.query.probe_at_position(.1,.3,.7,dataset=ds0)
        fr1.activate()
        res_b = tp.data.query.probe_at_position(.1,.3,.7,frame=fr0)
        fr1.activate()
        res_c = tp.data.query.probe_at_position(.1,.3,.7,dataset=ds0,frame=fr0)

        self.assertTrue(np.allclose(res_a.data,res_b.data))
        self.assertEqual(res_a.cell, res_b.cell)
        self.assertEqual(res_a.zone, res_b.zone)

        self.assertTrue(np.allclose(res_a.data,res_c.data))
        self.assertEqual(res_a.cell, res_c.cell)
        self.assertEqual(res_a.zone, res_c.zone)

    def test_non_successful_probe_at_position(self):
        ds0 = tp.data.load_tecplot(self.filenames['3x3x3_p'],
                        read_data_option=ReadDataOption.ReplaceInActiveFrame)
        self.assertIsNone(tp.data.query.probe_at_position(-1,0,0))

    def test_assertions(self):
        if __debug__:
            ds = tp.data.load_tecplot(self.filenames['3x3x3_p'])
            with self.assertRaises(TecplotLogicError):
                tp.data.query.probe_at_position(1,2,3,starting_cell=(1,2,3))
            with self.assertRaises(TecplotLogicError):
                tp.data.query.probe_at_position(1,2,3,starting_zone=ds.zone(0))
            with self.assertRaises(TecplotValueError):
                fr = tp.active_page().add_frame()
                tp.data.query.probe_at_position(1,2,3,frame=fr,dataset=ds)

    def test_assert_on_xyline(self):
        tp.new_layout()
        with loaded_sample_layout('3pt_xyline_text') as dataset:
            with self.assertRaises((TecplotLogicError, TecplotSystemError)):
                tp.data.query.probe_at_position(1,2)

    def test_interrupt(self):
        with loaded_sample_data('3x3x3_p'):
            with patch_tecutil('InterruptCheck', return_value=True):
                with self.assertRaises(TecplotInterruptError):
                    tp.data.query.probe_at_position(0,0,1000)

            with patch_tecutil('InterruptCheck', side_effect=AttributeError):
                self.assertIsNone(tp.data.query.probe_at_position(0,0,1000))

    def test_exception(self):
        with loaded_sample_data('3x3x3_p'):
            with patch_tecutil('ProbeAtPosition',
                               side_effect=TecplotSystemError('Assertion')):
                with self.assertRaises(TecplotSystemError):
                    tp.data.query.probe_at_position(0,0,1000)

            with patch_tecutil('ProbeAtPosition',
                               side_effect=TecplotSystemError):
                self.assertIsNone(tp.data.query.probe_at_position(0,0,1000))


class TestProbeOnSurface(unittest.TestCase):

    @skip_if_sdk_version_before(2018, 1)
    def setUp(self):
        pass

    def test_plottype_must_be_cart3d(self):
        tp.new_layout()
        fr = tp.active_frame()
        ds = fr.create_dataset('D', ['x', 'y', 'z', 's', 't'])
        zn = ds.add_fe_zone(ZoneType.FETriangle, 'Z', 3, 1)
        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            res = tp.data.query.probe_on_surface([[0],[0],[0]])

    def test_variables(self):
        tp.new_layout()
        fr = tp.active_frame()
        ds = fr.create_dataset('D', ['x', 'y', 'z', 's', 't'])
        zn = ds.add_fe_zone(ZoneType.FETriangle, 'Z', 3, 1)
        fr.plot_type = PlotType.Cartesian3D

        nodes = [[0  , 0, 0],
                 [1  , 0, 0],
                 [0.5, 0, np.sqrt(2)/2],]
        conn = [[0,1,2]]

        zn.values('x')[:] = [n[0] for n in nodes]
        zn.values('y')[:] = [n[1] for n in nodes]
        zn.values('z')[:] = [n[2] for n in nodes]
        zn.values('s')[:] = [0,1,2]
        zn.values('t')[:] = [0,0,1]

        zn.nodemap[:] = conn

        points = np.array([
            [0, 0, np.sqrt(2)/4],
            [0.5, 0, 0.2],
            [0.5, 0, 1.0],
            [0.5, 0.2, 0.2],
            ])
        expected = [
            [ 0.23570226,  0.66666667],
            [ 0.2,         0.92426408],
            [ 0.70710677,  2.        ],
            [ 0.2,         0.92426408]]

        v,cells,planes,zones = tp.data.query.probe_on_surface(points.T,
            variables=[2,3])
        vv = np.array(v).reshape((-1, len(points)))

        for ex, v, c, p, z in zip(expected, vv.T, cells, planes, zones):
            for i in range(2):
                self.assertAlmostEqual(v[i], ex[i])
            self.assertEqual(c, 0)
            self.assertEqual(p, IJKPlanes.Unused)
            self.assertEqual(z, ds.zone(0))

    def test_transient(self):
        tp.new_layout()
        fr = tp.active_frame()
        ds = fr.create_dataset('D', ['x', 'y', 'z', 's', 't'])
        zn0 = ds.add_fe_zone(ZoneType.FETriangle, 'Z', 3, 1)
        fr.plot_type = PlotType.Cartesian3D

        nodes = [[0  , 0, 0],
                 [1  , 0, 0],
                 [0.5, 0, np.sqrt(2)/2],]
        conn = [[0,1,2]]

        zn0.values('x')[:] = [n[0] for n in nodes]
        zn0.values('y')[:] = [n[1] for n in nodes]
        zn0.values('z')[:] = [n[2] for n in nodes]
        zn0.values('s')[:] = [0,1,2]
        zn0.values('t')[:] = [0,0,1]
        zn0.nodemap[:] = conn
        zn0.strand = 1
        zn0.solution_time = 1

        zn1 = ds.add_fe_zone(ZoneType.FETriangle, 'Z', 3, 1)

        zn1.values('x')[:] = [n[0] for n in nodes]
        zn1.values('y')[:] = [n[1] + 1 for n in nodes]
        zn1.values('z')[:] = [n[2] for n in nodes]
        zn1.values('s')[:] = [10,11,12]
        zn1.values('t')[:] = [-5,-5,-10]
        zn1.nodemap[:] = conn
        zn1.strand = 2
        zn1.solution_time = 2

        fr.plot().active_fieldmaps += [zn0, zn1]

        fr.plot().solution_time = 1

        points = np.array([
            [0, 0, np.sqrt(2)/4],
            [0.5, 0, 0.2],
            [0.5, 0, 1.0],
            [0.5, 0.2, 0.2],
            ])
        expected = [
            [ 0.16666667,  0.,          0.23570226,  0.66666667,  0.33333334],
            [ 0.5,         0.,          0.2,         0.92426408,  0.28284272],
            [ 0.5,         0.,          0.70710677,  2.,          1.        ],
            [ 0.5,         0.,          0.2,         0.92426408,  0.28284272]]

        v,cells,planes,zones = tp.data.query.probe_on_surface(points.T)
        vv = np.array(v).reshape((-1, len(points)))

        for ex, v, c, p, z in zip(expected, vv.T, cells, planes, zones):
            for i in range(2):
                self.assertAlmostEqual(v[i], ex[i])
            self.assertEqual(c, 0)
            self.assertEqual(p, IJKPlanes.Unused)
            self.assertEqual(z, ds.zone(0))

        fr.plot().solution_time = 2

        points = np.array([
            [0, 0, np.sqrt(2)/4],
            [0.5, 0, 0.2],
            [0.5, 0, 1.0],
            [0.5, 0.2, 0.2],
            ])
        expected = [
            [0.166666667, 1.0, 0.2357022577, 10.66666667, -6.66666667],
            [0.5, 1.0, 0.2, 10.9242640759729, -6.4142135865763299],
            [0.5, 1.0, 0.707106769, 12.0, -10.0],
            [0.5, 1.0, 0.2, 10.9242640759729, -6.4142135865763299]]

        v,cells,planes,zones = tp.data.query.probe_on_surface(points.T)
        vv = np.array(v).reshape((-1, len(points)))

        for ex, v, c, p, z in zip(expected, vv.T, cells, planes, zones):
            for i in range(5):
                self.assertAlmostEqual(v[i], ex[i])
            self.assertEqual(c, 0)
            self.assertEqual(p, IJKPlanes.Unused)
            self.assertEqual(z, ds.zone(1))

    def test_value_blanking(self):
        nodes = (
            ( 0  ,  0  , 0  ),
            (-0.4, -0.4, 0.5),
            ( 0  ,  0  , 0.5),
            ( 0.4,  0.4, 0.5),
            (-0.2, -0.2, 1  ),
            ( 0.2,  0.2, 1  ))
        scalar_data = (0, 1, 2, 3, 4, 5)
        conn = (
            (0, 3, 1),
            (1, 2, 4),
            (2, 3, 5),
            (2, 5, 4))
        neighbors = (
            (None, [1,2], None),
            (0, None, None),
            (0, None, None),
            (None, None, None))
        obscures = (True, True, True, False)

        tp.new_layout()
        fr = tp.active_frame()
        ds = fr.create_dataset('D', ['x', 'y', 'z', 's', 't'])
        z = ds.add_fe_zone(ZoneType.FETriangle,
                            name='FE Triangle Float (6,4) Nodal',
                            num_points=len(nodes), num_elements=len(conn),
                            face_neighbor_mode=FaceNeighborMode.LocalOneToMany)
        fr.plot_type = PlotType.Cartesian3D

        z.values('x')[:] = [n[0] for n in nodes]
        z.values('y')[:] = [n[1] for n in nodes]
        z.values('z')[:] = [n[2] for n in nodes]
        z.nodemap[:] = conn
        z.values('s')[:] = scalar_data
        z.face_neighbors.set_neighbors(neighbors, obscures=obscures)

        tp.macro.execute_command('''
            $!Blanking Value{Include = Yes}
            $!Blanking Value{ValueBlankCellMode = AnyCorner}
            $!Blanking Value{Constraint 1 {Include = Yes}}
            $!Blanking Value{Constraint 1 {VarA = 2}}
            $!Blanking Value{Constraint 1 {RelOp = GreaterThanOrEqual}}
            $!Blanking Value{Constraint 1 {ConstraintOp2Mode = UseConstant}}
            $!Blanking Value{Constraint 1 {ValueCutoff = 0.3}}
        ''')

        points = np.array([
            [-0.3,-0.3,0.5],
            [-0.5,-0.5,0],
            [0, 0, 0.25],
            ])
        expected = [
            [-0.3, -0.3, 0.5, 1.25, 0.0],
            [-0.4, -0.4, 0.5, 1.0, 0.0],
            [0.0, 0.0, 0.5, 2.0, 0.0]]

        v,cells,planes,zones = tp.data.query.probe_on_surface(points.T,
                                    probe_nearest=ProbeNearest.Position)
        vv = np.array(v).reshape((-1, len(points)))

        for ex, v, c, p, z in zip(expected, vv.T, cells, planes, zones):
            for i in range(5):
                self.assertAlmostEqual(v[i], ex[i])
            self.assertEqual(c, 1)
            self.assertEqual(p, IJKPlanes.Unused)
            self.assertEqual(z, ds.zone(0))

    def test_fe_triangle(self):
        tp.new_layout()
        fr = tp.active_frame()
        ds = fr.create_dataset('D', ['x', 'y', 'z', 's', 't'])
        zn = ds.add_fe_zone(ZoneType.FETriangle, 'Z', 3, 1)
        fr.plot_type = PlotType.Cartesian3D

        nodes = [[0  , 0, 0],
                 [1  , 0, 0],
                 [0.5, 0, np.sqrt(2)/2],]
        conn = [[0,1,2]]

        zn.values('x')[:] = [n[0] for n in nodes]
        zn.values('y')[:] = [n[1] for n in nodes]
        zn.values('z')[:] = [n[2] for n in nodes]
        zn.values('s')[:] = [0,1,2]
        zn.values('t')[:] = [0,0,1]

        zn.nodemap[:] = conn

        points = np.array([
            [0, 0, np.sqrt(2)/4],
            [0.5, 0, 0.2],
            [0.5, 0, 1.0],
            [0.5, 0.2, 0.2],
            ])
        expected = [
            [ 0.16666667,  0.,          0.23570226,  0.66666667,  0.33333334],
            [ 0.5,         0.,          0.2,         0.92426408,  0.28284272],
            [ 0.5,         0.,          0.70710677,  2.,          1.        ],
            [ 0.5,         0.,          0.2,         0.92426408,  0.28284272]]

        v,cells,planes,zones = tp.data.query.probe_on_surface(points.T, probe_nearest=ProbeNearest.Position)
        vv = np.array(v).reshape((-1, len(points)))

        for ex, v, c, p, z in zip(expected, vv.T, cells, planes, zones):
            for i in range(5):
                self.assertAlmostEqual(v[i], ex[i])
            self.assertEqual(c, 0)
            self.assertEqual(p, IJKPlanes.Unused)
            self.assertEqual(z, ds.zone(0))

    def test_fe_triangle_nodes(self):
        tp.new_layout()
        fr = tp.active_frame()
        ds = fr.create_dataset('D', ['x', 'y', 'z', 's', 't'])
        zn = ds.add_fe_zone(ZoneType.FETriangle, 'Z', 3, 1)
        fr.plot_type = PlotType.Cartesian3D

        nodes = [[0  , 0, 0],
                 [1  , 0, 0],
                 [0.5, 0, np.sqrt(2)/2],]
        conn = [[0,1,2]]

        zn.values('x')[:] = [n[0] for n in nodes]
        zn.values('y')[:] = [n[1] for n in nodes]
        zn.values('z')[:] = [n[2] for n in nodes]
        zn.values('s')[:] = [0,1,2]
        zn.values('t')[:] = [0,0,1]

        zn.nodemap[:] = conn

        points = np.array([
            [-1, -1, -1],
            [1.1,-0.1,-0.1],
            [0.5, 100, 1.0],
            [0.5, -1, -1],
            [1, 1, 0.1],
            [0.1, 0.1, 0.1],
            [0.1,0.1,0.1],
            [0.9,0.05,0.05],
            [0.5,0,0.2],
            ])
        expected = [
            [ 0. , 0., 0., 0., 0.],
            [ 1. , 0., 0., 1., 0.],
            [ 0.5, 0., 0.70710677, 2., 1.],
            [ 0. , 0., 0., 0., 0.],
            [ 1. , 0., 0., 1., 0.],
            [ 0. , 0., 0., 0., 0.],
            [ 0. , 0., 0., 0., 0.],
            [ 1. , 0., 0., 1., 0.],
            [ 0.5, 0., 0.70710677, 2., 1.]]
        expected_nodes = [0,1,2,0,1,0,0,1,2]

        v,nodes,planes,zones = tp.data.query.probe_on_surface(points.T,
            probe_nearest=ProbeNearest.Node)
        vv = np.array(v).reshape((-1, len(points)))

        for ex, v, exn, n, p, z in zip(expected, vv.T, expected_nodes, nodes,
                                       planes, zones):
            for i in range(5):
                self.assertAlmostEqual(v[i], ex[i])
            self.assertEqual(n, exn)
            self.assertEqual(p, IJKPlanes.Unused)
            self.assertEqual(z, ds.zone(0))

    def test_fe_triangle_offset(self):
        tp.new_layout()
        fr = tp.active_frame()
        ds = fr.create_dataset('D', ['x', 'y', 'z', 's', 't'])
        zn = ds.add_fe_zone(ZoneType.FETriangle, 'Z', 3, 1)
        fr.plot_type = PlotType.Cartesian3D

        nodes = [[10, 20, 5],
                 [5, 10, 5],
                 [10, 10, 10]]
        conn = [[0,1,2]]

        zn.values('x')[:] = [n[0] for n in nodes]
        zn.values('y')[:] = [n[1] for n in nodes]
        zn.values('z')[:] = [n[2] for n in nodes]
        zn.values('s')[:] = [0,1,2]
        zn.values('t')[:] = [0,0,1]

        zn.nodemap[:] = conn

        points = np.array([
            [8, 13, 7],
            [8, 13, 5],
            [8, 13, 0],
            [11, 21, 5],
            [6, 20, 5],
            [11,9,11],
            ])
        expected = [
            [8.22222222, 12.88888889, 6.77777778, 1.06666667, 0.35555556],
            [7.33333333, 13.33333333, 5.66666667, 0.8, 0.13333333],
            [6.8, 13.6, 5., 0.64, 0., ],
            [10., 20., 5., 0., 0.],
            [9.2, 18.4, 5., 0.16, 0., ],
            [10., 10., 10., 2., 1.]]

        v,cells,planes,zones = tp.data.query.probe_on_surface(points.T)
        vv = np.array(v).reshape((-1, len(points)))

        for ex, v, c, p, z in zip(expected, vv.T, cells, planes, zones):
            for i in range(5):
                self.assertAlmostEqual(v[i], ex[i])
            self.assertEqual(c, 0)
            self.assertEqual(p, IJKPlanes.Unused)
            self.assertEqual(z, ds.zone(0))

    def test_fe_triangle_small_near_zero(self):
        tp.new_layout()
        fr = tp.active_frame()
        ds = fr.create_dataset('D', ['x', 'y', 'z', 's', 't'])
        zn = ds.add_fe_zone(ZoneType.FETriangle, 'Z', 3, 1)
        fr.plot_type = PlotType.Cartesian3D

        scale = 1e-30
        nodes = np.array([[0  , 0, 0],
                          [1  , 0, 0],
                          [0.5, 0, np.sqrt(2)/2],]) * scale
        conn = [[0,1,2]]

        zn.values('x')[:] = [n[0] for n in nodes]
        zn.values('y')[:] = [n[1] for n in nodes]
        zn.values('z')[:] = [n[2] for n in nodes]
        zn.values('s')[:] = np.array([0,1,2]) * scale
        zn.values('t')[:] = np.array([0,0,1]) * scale

        zn.nodemap[:] = conn

        points = np.array([
            [0, 0, np.sqrt(2)/4],
            ]) * scale
        expected = np.array([
            [ 0.16666667,  0.,          0.23570226,  0.66666667,  0.33333334],
            ]) * scale

        v,cells,planes,zones = tp.data.query.probe_on_surface(points.T, tolerance=1e-5)
        vv = np.array(v).reshape((-1, len(points)))

        for ex, v, c, p, z in zip(expected, vv.T, cells, planes, zones):
            for i in range(5):
                self.assertAlmostEqual(v[i], ex[i])
            self.assertEqual(c, 0)
            self.assertEqual(p, IJKPlanes.Unused)
            self.assertEqual(z, ds.zone(0))

    def test_fe_quad(self):
        tp.new_layout()
        fr = tp.active_frame()
        ds = fr.create_dataset('D', ['x', 'y', 'z', 's', 't'])
        zn = ds.add_fe_zone(ZoneType.FEQuad, 'Z', 4, 1)
        fr.plot_type = PlotType.Cartesian3D

        nodes = [[0  , 0, 0],
                 [1  , 0, 0],
                 [0.5, 0, np.sqrt(2)/2],
                 [0, 0, 1]]
        conn = [[0,1,2,3]]

        zn.values('x')[:] = [n[0] for n in nodes]
        zn.values('y')[:] = [n[1] for n in nodes]
        zn.values('z')[:] = [n[2] for n in nodes]
        zn.values('s')[:] = [0,1,2,3]
        zn.values('t')[:] = [0,0,2,2]

        zn.nodemap[:] = conn

        points = np.array([
            [-0.5, 0, np.sqrt(2)/4],
            [0.5, 0, 0.2],
            [0.5, 0, 1.0],
            [0.75, 0, 1.0],
            [0.5, 0.2, 0.2],
            ])
        expected = [
            [ 0.        , 0.        , 0.35355339, 1.06066017, 0.70710678],
            [ 0.5       , 0.        , 0.2       , 1.01213204, 0.48284272],
            [ 0.37226041, 0.        , 0.78193489, 2.25547918, 2.        ],
            [ 0.5       , 0.        , 0.70710677, 2.        , 2.        ],
            [ 0.5       , 0.        , 0.2       , 1.01213204, 0.48284272]]

        v,cells,planes,zones = tp.data.query.probe_on_surface(points.T)
        vv = np.array(v).reshape((-1, len(points)))

        for ex, v, c, p, z in zip(expected, vv.T, cells, planes, zones):
            for i in range(5):
                self.assertAlmostEqual(v[i], ex[i])
            self.assertEqual(c, 0)
            self.assertEqual(p, IJKPlanes.Unused)
            self.assertEqual(z, ds.zone(0))


    def test_poly_triangle(self):
        tp.new_layout()
        fr = tp.active_frame()

        nodes = [[0  , 0, 0],
                 [1  , 0, 0],
                 [0.5, 0, np.sqrt(2)/2],]
        elementmap = ((0, 1, 2), )

        num_faces = len(set( tuple(sorted([e[i], e[(i+1)%len(e)]]))
                             for e in elementmap for i in range(len(e)) ))

        ds = fr.create_dataset('D', ['x', 'y', 'z', 's', 't'])
        zn = ds.add_poly_zone(ZoneType.FEPolygon, name='Z',
                              num_points=len(nodes),
                              num_elements=len(elementmap),
                              num_faces=num_faces)

        fm = zn.facemap
        fm.set_elementmap(elementmap)

        zn.values('x')[:] = [n[0] for n in nodes]
        zn.values('y')[:] = [n[1] for n in nodes]
        zn.values('z')[:] = [n[2] for n in nodes]
        zn.values('s')[:] = [0,1,2]
        zn.values('t')[:] = [0,0,1]

        fr.plot_type = PlotType.Cartesian3D

        points = np.array([
            [0, 0, np.sqrt(2)/4],
            [0.5, 0, 0.2],
            [0.5, 0, 1.0],
            [0.5, 0.2, 0.2],
            ])
        expected = [
            [ 0.16666667,  0.,          0.23570226,  0.66666667,  0.33333334],
            [ 0.5,         0.,          0.2,         0.92426408,  0.28284272],
            [ 0.5,         0.,          0.70710677,  2.,          1.        ],
            [ 0.5,         0.,          0.2,         0.92426408,  0.28284272]]

        v,cells,planes,zones = tp.data.query.probe_on_surface(points.T)
        vv = np.array(v).reshape((-1, len(points)))

        for ex, v, c, p, z in zip(expected, vv.T, cells, planes, zones):
            for i in range(5):
                self.assertAlmostEqual(v[i], ex[i])
            self.assertEqual(c, 0)
            self.assertEqual(p, IJKPlanes.Unused)
            self.assertEqual(z, ds.zone(0))

    def test_ordered_quad(self):
        tp.new_layout()
        fr = tp.active_frame()
        ds = fr.create_dataset('D', ['x', 'y', 'z', 's', 't'])
        zn = ds.add_ordered_zone('Z', (2, 2))
        fr.plot_type = PlotType.Cartesian3D

        nodes = [[0  , 0, 0],
                 [1  , 0, 0],
                 [0, 0, 1],
                 [0.5, 0, np.sqrt(2)/2],]

        zn.values('x')[:] = [n[0] for n in nodes]
        zn.values('y')[:] = [n[1] for n in nodes]
        zn.values('z')[:] = [n[2] for n in nodes]
        zn.values('s')[:] = [0,1,3,2]
        zn.values('t')[:] = [0,0,2,2]

        points = np.array([
            [-0.5, 0, np.sqrt(2)/4],
            [0.5, 0, 0.2],
            [0.5, 0, 1.0],
            [0.75, 0, 1.0],
            [0.5, 0.2, 0.2],
            ])
        expected = [
            [ 0.        , 0.        , 0.35355339, 1.06066017, 0.70710678],
            [ 0.5       , 0.        , 0.2       , 1.01213204, 0.48284272],
            [ 0.37226041, 0.        , 0.78193489, 2.25547918, 2.        ],
            [ 0.5       , 0.        , 0.70710677, 2.        , 2.        ],
            [ 0.5       , 0.        , 0.2       , 1.01213204, 0.48284272]]

        v,cells,planes,zones = tp.data.query.probe_on_surface(points.T)
        vv = np.array(v).reshape((-1, len(points)))

        for ex, v, c, p, z in zip(expected, vv.T, cells, planes, zones):
            for i in range(5):
                self.assertAlmostEqual(v[i], ex[i])
            self.assertEqual(c, 0)
            self.assertEqual(p, IJKPlanes.K)
            self.assertEqual(z, ds.zone(0))

    def test_fe_lineseg(self):
        tp.new_layout()
        fr = tp.active_frame()
        ds = fr.create_dataset('D', ['x', 'y', 'z', 's', 't'])
        zn = ds.add_fe_zone(ZoneType.FELineSeg, 'Z', 3, 2)
        fr.plot_type = PlotType.Cartesian3D

        nodes = [[0, 0, 0],
                 [1, 0, 1],
                 [1, 1, 1]]
        conn = [[0,1], [1,2]]

        zn.values('x')[:] = [n[0] for n in nodes]
        zn.values('y')[:] = [n[1] for n in nodes]
        zn.values('z')[:] = [n[2] for n in nodes]
        zn.values('s')[:] = [0,1,2]
        zn.values('t')[:] = [0,0,2]
        zn.nodemap[:] = conn

        points = np.array([
            [0,0.1,0],
            [1,0.1,1],
            [1,1.1,1],
            ])
        expected = [[0, 0, 0, 0, 0],
                    [1, 0, 1, 1, 0],
                    [1, 1, 1, 2, 2]]
        expected_nodes = [0, 1, 2]

        v,nodes,planes,zones = tp.data.query.probe_on_surface(points.T,
                                                              zones=[zn])
        vv = np.array(v).reshape((-1, len(points)))

        for ex, exc, v, c, p, z in zip(expected, expected_nodes, vv.T, nodes,
                                       planes, zones):
            for i in range(5):
                self.assertAlmostEqual(v[i], ex[i])
            self.assertEqual(c, exc)
            self.assertEqual(p, IJKPlanes.Unused)
            self.assertEqual(z, ds.zone(0))

    def test_ordered_line(self):
        tp.new_layout()
        fr = tp.active_frame()
        ds = fr.create_dataset('D', ['x', 'y', 'z', 's', 't'])
        zn = ds.add_ordered_zone('Z', (3,))
        fr.plot_type = PlotType.Cartesian3D

        nodes = [[0, 0, 0],
                 [1, 0, 1],
                 [1, 1, 1]]

        zn.values('x')[:] = [n[0] for n in nodes]
        zn.values('y')[:] = [n[1] for n in nodes]
        zn.values('z')[:] = [n[2] for n in nodes]
        zn.values('s')[:] = [0,1,2]
        zn.values('t')[:] = [0,0,2]

        points = np.array([
            [0,0.1,0],
            [1,0.1,1],
            [1,1.1,1],
            ])
        expected = [[0, 0, 0, 0, 0],
                    [1, 0, 1, 1, 0],
                    [1, 1, 1, 2, 2]]
        expected_nodes = [0, 1, 2]

        v,nodes,planes,zones = tp.data.query.probe_on_surface(points.T,
                                                              zones=[zn])
        vv = np.array(v).reshape((-1, len(points)))

        for ex, exc, v, c, p, z in zip(expected, expected_nodes, vv.T, nodes,
                                       planes, zones):
            for i in range(5):
                self.assertAlmostEqual(v[i], ex[i])
            self.assertEqual(c, exc)
            self.assertEqual(p, IJKPlanes.Unused)
            self.assertEqual(z, ds.zone(0))

    def test_ordered_point(self):
        tp.new_layout()
        fr = tp.active_frame()
        ds = fr.create_dataset('D', ['x', 'y', 'z', 's', 't'])
        zn = ds.add_ordered_zone('Z', (1,))
        fr.plot_type = PlotType.Cartesian3D

        nodes = [[0.5, 0, np.sqrt(2)/2],]

        zn.values('x')[:] = [n[0] for n in nodes]
        zn.values('y')[:] = [n[1] for n in nodes]
        zn.values('z')[:] = [n[2] for n in nodes]
        zn.values('s')[:] = [1]
        zn.values('t')[:] = [2]

        points = np.array([
            [0,0,0]
            ])
        expected = [
            [ 0.5       , 0.        , 0.70710677, 1.        , 2.        ],]

        v,cells,planes,zones = tp.data.query.probe_on_surface(points.T,
                                                              zones=[zn])
        vv = np.array(v).reshape((-1, len(points)))

        for ex, v, c, p, z in zip(expected, vv.T, cells, planes, zones):
            for i in range(5):
                self.assertAlmostEqual(v[i], ex[i])
            self.assertEqual(c, 0)
            self.assertEqual(p, IJKPlanes.Unused)
            self.assertEqual(z, ds.zone(0))


if __name__ == '__main__':
    from .. import main
    main()
