# -*- encoding: utf-8 -*-
import pkg_resources
import re
from distutils.version import LooseVersion

from .exceptions import MissingPackageError, IncorrectPackageVersionError

SUBPATTERN = r'((?P<operation%d>==|>=|>|<)(?P<version%d>(\d+)?(\.[a-zA-Z0-9]+)?(\.\d+)?))'
RE_PATTERN = re.compile(
    r'^(?P<name>[\w\-]+)%s?(,%s)?$' % (SUBPATTERN % (1, 1), SUBPATTERN % (2, 2)))


def verify_packages(packages):
    if not packages:
        return
    if isinstance(packages, str):
        packages = packages.splitlines()

    for package in packages:
        if not package:
            continue

        match = RE_PATTERN.match(package)
        if match:
            name = match.group('name')
            operation = match.group('operation1')
            version = match.group('version1')
            _verify_package(name, operation, version)
            operation2 = match.group('operation2')
            version2 = match.group('version2')
        else:
            raise ValueError('Unable to read requirement: %s' % package)


def _verify_package(name, operation, version):
    try:
        module = pkg_resources.get_distribution(name)
    except pkg_resources.DistributionNotFound:
        raise MissingPackageError(name)

    if not operation:
        return

    required_version = LooseVersion(version)
    installed_version = LooseVersion(module.version)

    if operation == '==':
        check = required_version == installed_version
    elif operation == '>':
        check = installed_version > required_version
    elif operation == '>=':
        check = installed_version > required_version or \
                installed_version == required_version
    else:
        raise NotImplementedError(
            'operation \'%s\' is not supported' % operation)
    if not check:
        raise IncorrectPackageVersionError(name, installed_version, operation,
                                           required_version)



