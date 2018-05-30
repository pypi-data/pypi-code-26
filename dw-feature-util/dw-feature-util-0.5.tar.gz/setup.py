try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from setuptools import find_packages


setup(name='dw-feature-util',
      version='0.5',
      description='Stock feature producers',
      author='Daniel Wang',
      author_email='danielwpz@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['tests*']),
      install_requires=[
          'dw-datasource',
          'pandas',
          'numpy'
      ],
      zip_safe=False)
