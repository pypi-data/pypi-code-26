from os.path import abspath, dirname, join
from setuptools import setup

__version__ = '1.0.10'


def read_file(filename):
    """Get the contents of a file"""
    here = abspath(dirname(__file__))
    with open(join(here, filename), encoding='utf-8') as f:
        return f.read()


setup(name='hatchbuck',
      version=__version__,
      description='Hatchbuck.com CRM API bindings for Python',
      long_description=read_file('README.rst'),
      keywords=['hatchbuck', 'CRM', 'API'],
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      url='https://github.com/vshn/python-hatchbuck',
      author='VSHN AG, Bashar Said',
      author_email='bashar.said@vshn.ch',
      license='BSD',
      py_modules=['hatchbuck'],
      install_requires=[
          'requests>=2',
          'pycountry>=1',
      ])
