# Copyright Okera Inc.


# pylint: disable=wrong-import-order

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# Import the public API
from okera.odas import context, version
