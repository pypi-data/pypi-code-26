#!/usr/bin/env python3

from setuptools import setup

# Work around mbcs bug in distutils.
# http://bugs.python.org/issue10945
import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    codecs.register(lambda name, enc=ascii: {True: enc}.get(name == 'mbcs'))

VERSION = '0.1.33'

setup(
    name='gravity-protocol',
    version=VERSION,
    description='Python library for the Gravity Protocol Blockchain network',
    long_description=open('README.md').read(),
    download_url='https://github.com/Keegan-lee/python-gravity/tarball/' + VERSION,
    author='Keegan Francis',
    author_email='keegan.lee.francis@gmail.com',
    maintainer='Keegan Francis',
    maintainer_email='keegan.lee.francis@gmail.com',
    url='https://github.com/keegan-lee/gravity-python',
    keywords=['gravity', 'library', 'api', 'rpc'],
    packages=[
        "gravity",
        "gravity.cli",
        "gravityapi",
        "gravitybase",
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Games/Entertainment',
    ],
    entry_points={
        'console_scripts': [
            'gravity = gravity.cli.cli:main',
        ],
    },
    install_requires=[
        "graphenelib>=0.6.2",
        "appdirs",
        "prettytable",
        "events==0.3",
        "scrypt",
        "pycryptodome",  # for AES, installed through graphenelib already
        # for the CLI tool
        "click",
        "treelib",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    include_package_data=True,
)
