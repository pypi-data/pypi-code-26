# Copyright 2017 Shortest Track Company. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.

# To publish to PyPi use: python setup.py bdist_wheel upload -r pypi

from setuptools import setup, find_packages

version = '1.0.19'

setup(
    name='st-dataprovider',
    version=version,
    packages=find_packages(),
    description='shortest track dataprovider',
    author='Fugui Xing',
    author_email='admin@shortesttrack.com',
    url='https://github.com/shortesttrack/dataprovider-py',
    download_url='https://github.com/shortesttrack/dataprovider-py/archive/v1.0.19',
    keywords=[
        'Shortest Track',
        'st_library',
        'dataprovider'
    ],
    license="Apache Software License",
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    long_description="""\
Support package for Shortest Track Library. This provides Python APIs
for accessing Shortest Track Platform services such as structured data storage.
  """,
    install_requires=[
        'requests-toolbelt==0.8.0',
        'pandas==0.19.1',
        'urlobject==2.4.3',
        'six==1.11.0',
        'python-dateutil==2.7.0',
        'PyJWT==1.6.1',
        'cryptography==2.2.1',
        'mock==2.0.0',
        'pytz==2018.3',
        'psycopg2-binary==2.7.4',
        'redis==2.10.6',
        'backoff==1.5.0'
    ]
)
