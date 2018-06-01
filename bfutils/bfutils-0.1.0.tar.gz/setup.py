from setuptools import setup
import os

data = os.path.join( os.path.dirname( __file__ ), 'bfutils', 'data')

setup(
    name='bfutils',
    version='0.1.0',
    author='Landon T. Clipp',
    author_email='clipp2@illinois.edu',
    packages=['bfutils'],
    description='Basic Fusion utilities',
    long_description='bfutils provides a few useful utilities for \
    interacting with the Basic Fusion data product.',
    install_requires=[ 'pyyaml' ],
    url = 'https://github.com/TerraFusion/bfutils',
    keywords= ['bfutils', 'bf', 'utilities', 'nasa', 'eos', 'earth'],
    package_data = {'bfutils': 
        [ os.path.join( data, 'config.yml'), 
        os.path.join( data, 'Orbit_Path_Time.json'),
        os.path.join( data, 'Orbit_Path_Time.txt')]},
    include_package_data = True,
)

