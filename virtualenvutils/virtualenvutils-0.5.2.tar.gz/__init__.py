# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

_package_data = dict(
    full_package_name='virtualenvutils',
    version_info=(0, 5, 2),
    __version__='0.5.2',
    author='Anthon van der Neut',
    author_email='a.van.der.neut@ruamel.eu',
    description='manage virtualenv based utilities',
    keywords='virtualenv utilities',
    entry_points='virtualenvutils=virtualenvutils.__main__:main',
    # entry_points=None,
    license='MIT License',
    since=2016,
    # status: "α|β|stable",  # the package status on PyPI
    # data_files="",
    universal=True,
    install_requires=[
        'ruamel.appconfig',
        'ruamel.std.argparse>=0.8',
        'ruamel.std.pathlib',
        'virtualenv',
    ],
    # py27=["ruamel.ordereddict"],
)


version_info = _package_data['version_info']
__version__ = _package_data['__version__']
