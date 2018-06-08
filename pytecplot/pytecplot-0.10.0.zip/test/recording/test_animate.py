import unittest
import tecplot as tp
from test.sample_data import sample_data
from .recording_util import *
from test import skip_if_connected, skip_if_sdk_version_before


def _check_animate_translation(translation):
    # Animate commands should translate to
    # execute macro command
    return 'macro.execute_command' in translation


class TestAnimate(unittest.TestCase):
    @skip_if_sdk_version_before(2017, 3)
    @skip_if_connected
    def setUp(self):
        tp.new_layout()
        sample_data('10x10x10')

    def test_slices(self):
        # Should not crash
        translated = translate('''
        $!AnimateSlices
            Start=1
            End=2
        ''')

        self.assertTrue(_check_animate_translation(translated))

    def test_linemaps(self):
        # Should not crash
        translated = translate('''
        $!AnimateLineMaps
            Start=1
            End=2
        ''')

        self.assertTrue(_check_animate_translation(translated))

    def test_contour_levels(self):
        # Should not crash
        translated = translate('''
        $!AnimateContourLevels
            Start=1
            End=2
        ''')
        self.assertTrue(_check_animate_translation(translated))

    def test_ijk_blanking(self):
        # Should not crash
        translated = translate('''
        $!AnimateIJKBlanking
            Start=1
            End=2
        ''')

        self.assertTrue(_check_animate_translation(translated))

    def test_ijk_planes(self):
        # Should not crash
        translated = translate('''
        $!AnimateIJKPlanes
            Start=1
            End=2
        ''')

        self.assertTrue(_check_animate_translation(translated))

    def test_isosurface(self):
        # Should not crash
        translated = translate('''
        $!AnimateIsoSurfaces
          StartValue = 0
          EndValue = .1
          NumSteps = 2
        ''')

        self.assertTrue(_check_animate_translation(translated))

    def test_stream(self):
        # Should not crash
        translated = translate('''
        $!AnimateStream
            Start=1
            End=2
        ''')

        self.assertTrue(_check_animate_translation(translated))

    def test_time(self):
        # Should not crash
        translated = translate('''
        $!AnimateTime
        ''')

        self.assertTrue(_check_animate_translation(translated))

    def test_zones(self):
        # Should not crash
        translated = translate('''
        $!AnimateZones
        ''')

        self.assertTrue(_check_animate_translation(translated))
