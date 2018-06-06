from distutils.core import setup
from setuptools import find_packages

setup(name='notifyexceptions',
      version='1.1',
      description=('Get exception on ADMINS mail IDs'),
      author='Shashank Shukla',
      author_email='shuklashashank@outlook.com',
      url='http://pypi.python.org/pypi/notifyexceptions',
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      install_requires =['Django>=1.8'],
     )
