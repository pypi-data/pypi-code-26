import os

from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='shinkendo',
    version='0.2.1',
    packages=find_packages(),
    description='A Shinken CLI.',
    author='Guillaume Subiron',
    author_email="maethor+pip@subiron.org",
    long_description=read('README.md'),
    include_package_data=True,
    url='http://github.com/sysnove/shinkendo',
    install_requires=[
        'Click',
        'Requests',
    ],
    py_modules=['shinkendo'],
    entry_points='''
        [console_scripts]
        shinkendo=shinkendo:main
    ''',
    license="WTFPL",
)
