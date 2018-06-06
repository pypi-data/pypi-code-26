from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(name='caseciteparser',
      version='1.0',
      description='A parser for legal case citations.',
      long_description=long_description,
      url='https://github.com/parthsagdeo/caseciteparser',
      author='Parth Sagdeo',
      author_email='caseciteparser@gmail.com')
