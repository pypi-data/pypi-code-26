from setuptools import setup

setup(name='travis_tester',
      version="0.0.7",
      description='Testing git and deployment stuff',
      long_description="Nothing",
      url='https://github.com/MatthewGilbert/testing',
      author='Matthew Gilbert',
      author_email='matthew.gilbert12@gmail.com',
      license='MIT',
      platforms='any',
      packages=['mypackage', 'mypackage.tests'],
      zip_safe=False)
