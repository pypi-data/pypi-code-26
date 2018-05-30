'''
Created on May 22, 2018

@author: David Steinberg
'''
import unittest
from sheepdog_exporter.exporter import Exporter


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testExporter(self):
        exporter = Exporter('./credentials.json', 'https://dcp.bionimbus.org')
        exporter.get_all_submissions('topmed', 'public')
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()