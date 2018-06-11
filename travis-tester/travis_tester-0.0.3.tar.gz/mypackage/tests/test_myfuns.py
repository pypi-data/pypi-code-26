import unittest
from mypackage import myfuns


class TestCubePk(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_myfun3_passing(self):
        val3 = myfuns.myfun_return3()
        self.assertEqual(val3, 3)
