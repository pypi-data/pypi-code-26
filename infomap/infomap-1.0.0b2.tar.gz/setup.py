# Always prefer setuptools over distutils
from setuptools import setup, find_packages, Extension
# To use a consistent encoding
from codecs import open
from os import path, walk
import fnmatch
import sys
import re

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


cppSources = []
for root, dirnames, filenames in walk('.'):
    for filename in fnmatch.filter(filenames, '*.cpp'):
        cppSources.append(path.join(root, filename))
    for filename in fnmatch.filter(filenames, '*.h'):
        cppSources.append(path.join(root, filename))

# Extract Infomap version
infomapVersion = ''
with open(path.join('src', 'io', 'version.cpp')) as f:
    for line in f:
        m = re.match(r'.+INFOMAP_VERSION = \"(.+)\"', line)
        if m: infomapVersion = m.groups()[0]

infomap_module = Extension(
    '_infomap',
    sources=cppSources,
    language='c++',
    extra_compile_args=[
        '-DAS_LIB',
        '-DPYTHON',
        '-Wno-deprecated-register',
        '-std=c++14',
        '-stdlib=libc++', # Fix error: no member named 'unique_ptr' in namespace 'std'
        '-mmacosx-version-min=10.10' # Fix clang: error: invalid deployment target for -stdlib=libc++ (requires OS X 10.7 or later)
    ],
    extra_link_args=[
        '-mmacosx-version-min=10.10'
    ])

setup(
    name='infomap',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.0.0-beta.2',

    description='Infomap network clustering algorithm.',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/mapequation/infomap',

    # Author details
    author='Daniel Edler',
    author_email='daniel.edler@umu.se',

    # Choose your license
    license='AGPL-3.0+',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',

        # Pick your license as you wish (should match "license" above)
        # 'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)'

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='network analysis community detection',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    packages=find_packages(),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    # install_requires=required,    

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    # }

    ext_modules=[infomap_module],
    py_modules=["infomap"]
)