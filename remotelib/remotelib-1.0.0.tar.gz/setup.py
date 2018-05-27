try:
    from distutils.core import setup
except ImportError:
    from setuptools import setup


from setuptools import find_packages

import os
import os.path

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

version = "1.0.0"

setup(
    name='remotelib',
    version=version,
    packages=["remotelib"],
    url='https://google.com',
    license='GPL',
    author='Martin Klapproth',
    author_email='martin.klapproth@googlemail.com',
    include_package_data=True,
    install_requires=[
        "ecdsa>=0.11",
        "paramiko>=1.15.2",
        "pycrypto>=2.6.1",
    ],
    description='Remotelib',
)
