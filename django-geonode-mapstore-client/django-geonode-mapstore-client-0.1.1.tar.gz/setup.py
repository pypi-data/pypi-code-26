import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'VERSION')) as version_file:
        version = version_file.read().strip()

setup(
    name='django-geonode-mapstore-client',
    version=version,
    author='Alessio Fabiani',
    author_email='alessio.fabiani@gmail.com',
    url='https://github.com/GeoNode/geonode-mapstore-client',
    description="Use GeoNode client in your django projects",
    long_description=open(os.path.join(here, 'README.md')).read(),
    license='BSD, see LICENSE file.',
    install_requires=[],

# adding packages
    packages=find_packages('geonode_mapstore_client'),
    package_dir = {'':'geonode_mapstore_client'},

    # trying to add files...
    include_package_data = True,
    package_data = {
        '': ['*.*'],
        '': ['static/*.*'],
        'static': ['*.*'],
        '': ['templates/*.*'],
        'templates': ['*.*'],
    },

    zip_safe = False,
    classifiers  = [],
)
