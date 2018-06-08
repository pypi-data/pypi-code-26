import unittest

import tecplot as tp

from .recording_util import *

from test.sample_data import sample_data
from test import skip_if_connected, skip_if_sdk_version_before


class TestFrameControl(unittest.TestCase):
    @skip_if_sdk_version_before(2017, 3)
    @skip_if_connected
    def setUp(self):
        pass

    def test_default_2d_streamtrace(self):
        self.assertFalse(translate(
            '$!FrameSetup Default2DStreamtrace{StartPos{X = -0.026138334325338908}}'))

    def test_default_3d_streamtrace(self):
        self.assertFalse(translate(
            '$!FrameSetup Default3DStreamtrace{StartPos{X = -0.026138334325338908}}'))

    def test_num_surface_points(self):
        self.assertFalse(translate(
            '$!FrameSetup NumStreamsurfacePoints = 20'))

    def test_vectdeflen(self):
        self.assertFalse(translate(
            '$!FrameSetup VectDefLen = 20'))

    def test_num_stream_rake_points(self):
        self.assertFalse(translate(
            '$!FrameSetup NumStreamRakePoints = 20'))

    def test_rod_ribbon_def_len(self):
        self.assertFalse(translate(
            '$!FrameSetup RodRibbonDefLen = 20'))

    def test_num_stream_surface_points(self):
        self.assertFalse(translate(
            '$!FrameSetup NumStreamSurfacePoints = 20'))
