import unittest
from calc_demo.calc_demo import Calc

class TestDiv(unittest.TestCase):
    def test_div(self):
        
        n1 = Calc(2,2)
        self.assertEquals(n1.div_call(),1)
