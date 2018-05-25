import pytest
import re
import sys
sys.path.append("..")
import emlid.deviceinfo
from .deviceinfostub import *


def test_vendor(device_information):
    assert device_information().vendor.strip() == 'Emlid Limited'


def test_product(device_information):
    product = device_information().product.strip()
    assert product == 'Stub'


def test_product_boot_without_hat(no_hat_device_information):
    product = no_hat_device_information().product
    assert product == 'Seems like you booted without Navio properly screwed!'


def test_vendor_boot_without_hat(no_hat_device_information):
    vendor = no_hat_device_information().vendor
    assert vendor == '¯\_(ツ)_/¯ Unknown, but most likely Emlid'


def test_no_issue(no_issue_device_information):
    with pytest.raises(emlid.deviceinfo.NotVersionControlledOSReleaseException):
        issue = no_issue_device_information().issue


def test_issue(device_information):
    validation_regexp = re.compile('^Emlid \d{4}[-/]\d{2}[-/]\d{2}.*')
    issue = device_information().issue
    assert validation_regexp.match(issue)


def test_kernel(device_information):
    kernel = device_information().kernel
    assert kernel == 'emlid-kernel-v7'


def test_repr(device_information):
    validation_regexp = re.compile("^Vendor: .*\nProduct: .*\nIssue: .*\nKernel: .*$")
    s = str(device_information())
    assert validation_regexp.match(s)
