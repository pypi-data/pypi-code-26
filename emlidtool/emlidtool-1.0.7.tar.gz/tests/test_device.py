import pytest
import sys
sys.path.append("..")
import emlid.devices.tester
from .devicestub import StubDevice

@pytest.fixture
def stub_tester():
    return emlid.devices.tester.Tester(StubDevice())

def test_all_tests(stub_tester):
    results = stub_tester.run_tests('all')
    assert results['PassingTest'].result == True and results['FailingTest'].result == False

def test_falling_test(stub_tester):
    results = stub_tester.run_tests('FailingTest')
    assert results['FailingTest'].result == False

def test_missing_test(stub_tester):
    with pytest.raises(Exception):
        stub_tester.run_tests('MissingTest')

def test_exception_handling_on_failed_test(stub_tester):
    test_name = 'FailingTestWithException'
    result = stub_tester.run_tests(test_name)
    assert result[test_name].result == False and result[test_name].description == "Test failed"
