#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    import setuptools
except ImportError:
    import distutils.core as setuptools

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, 'gwc', '__version__.py'), 'r') as f:
    exec(f.read(), about)

setuptools.setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    # long_description=readme,
    packages=setuptools.find_packages(),
    install_requires=['gdpy>=0.1.0', 'prettytable==0.7.2'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'gwc = gwc.gwc_scripts:main',
        ]
    },
    url=about['__url__'],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
