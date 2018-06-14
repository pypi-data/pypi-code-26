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
    packages=find_packages(),
    include_package_data = True,
    zip_safe = False,
    classifiers  = [],
)
