# -*- coding: utf-8 -*-
"""
goodreads_api_client.tests
~~~~~

Contains all test goodreads_api_client tests.
"""

import unittest


if __name__ == '__main__':
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('.', pattern='test_*.py')
    unittest.main(verbosity=2)
