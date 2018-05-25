import collections
from emlid.util.util import NotRootException

TestDesc = collections.namedtuple('TestDesc', ['cls', 'args'])
TestCase = collections.namedtuple('TestCase', ['name', 'descriptor'])
ResultDesc = collections.namedtuple('ResultDesc', ['result', 'description'])


class Tester:
    def __init__(self, device):
        self.device = device

    def run_tests(self, test_names):
        all_tests = self.device.get_all_tests()

        if test_names == 'all':
            tests = all_tests
        else:
            tests = [test for test in all_tests if test.name in test_names]
            if len(tests) == 0:
                raise Exception("No tests to run")

        results = {}
        for test in tests:
            results[test.name] = self.run_test(test)

        return results

    @staticmethod
    def run_test(test):
        try:
            test = test.descriptor.cls(**test.descriptor.args)
            result = ResultDesc(result=test.run(), description='Tramp')
        except NotRootException:
            result = ResultDesc(result=False, description='Please launch with sudo to run this test')
        except Exception as e:
            result = ResultDesc(result=False, description=str(e))
        return result
