# -*- coding: utf-8 -*-

import os
from setuptools import setup

requirements = [
    'tidegravity',
    'flask==1.0.2',
    'flask_restful==0.3.6',
    'marshmallow==2.15.3'
]

with open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'r') as fd:
    long_description = fd.read().strip()

setup(
    name='TideServer',
    version='0.2alpha-5',
    packages=['tideserver'],
    package_data={
        '': ['uwsgi.ini', 'wsgi.py', 'tideserver.service'],
    },
    include_package_data=True,
    data_files=[


    ],
    install_requires=requirements,
    python_requires='>=3.5.*',
    description="Flask REST API to supply tidal gravity corrections",
    long_description=long_description,
    author="Zachery Brady",
    author_email="bradyzp@dynamicgravitysystems.com",
    url="https://github.com/DynamicGravitySystems/TideFlaskServer",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux'
    ]
)
