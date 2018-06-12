from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='test_cool_package',
      version=version,
      description="Description",
      long_description="""\
Long description""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='Learning python',
      author='Taras Vaskiv',
      author_email='codertarasvaskiv@gmail.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
