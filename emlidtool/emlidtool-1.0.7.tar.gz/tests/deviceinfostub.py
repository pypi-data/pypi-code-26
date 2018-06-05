import pytest
import sys
sys.path.append("..")
import emlid.deviceinfo

@pytest.fixture
def device_information():
    DeviceInformation = emlid.deviceinfo.DeviceInformation
    DeviceInformation.vendor_path = "test_files/deviceinfo/vendor"
    DeviceInformation.product_path = "test_files/deviceinfo/product"
    DeviceInformation.issue_path = "test_files/deviceinfo/issue.txt"
    DeviceInformation._set_kernel = lambda s: 'emlid-kernel-v7'
    return DeviceInformation

@pytest.fixture
def no_hat_device_information():
    DeviceInformation = device_information()
    DeviceInformation.vendor_path = "test_files/deviceinfo/novendor"
    DeviceInformation.product_path = "test_files/deviceinfo/noproduct"
    return DeviceInformation

@pytest.fixture
def no_issue_device_information():
    DeviceInformation = device_information()
    DeviceInformation.issue_path = "test_files/deviceinfo/noissue"
    return DeviceInformation
