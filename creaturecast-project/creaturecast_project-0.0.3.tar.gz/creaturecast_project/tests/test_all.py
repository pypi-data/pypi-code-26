import sys
import unittest
import logging
import test_data


if __name__ == '__main__':

    debug = True
    logging.basicConfig(stream=sys.stderr)

    def create_suite():
        test_suite = unittest.TestSuite()
        tests = [
            test_data.DataTest
        ]
        for test in tests:
            if debug:
                logging.getLogger(test.__class__.__name__).setLevel(logging.DEBUG)
            test_suite.addTest(test())

        return test_suite

    suite = create_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)
