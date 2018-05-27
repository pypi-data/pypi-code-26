try:
    from distutils.core import setup
except ImportError:
    from setuptools import setup


import os.path

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

version = "0.9.1"

setup(
    name='testosterone-client',
    version=version,
    packages=["testosterone"],
    url='https://google.com',
    license='GPL',
    author='Martin Klapproth',
    author_email='martin.klapproth@googlemail.com',
    include_package_data=True,
    install_requires=[
        "requests",
        "mysqlclient",
    ],
    description='Testosterone end-2-end test framework',
)
