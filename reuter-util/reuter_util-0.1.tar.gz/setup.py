from setuptools import setup

setup(name='reuter_util',
      version='0.1',
      description='Utility functions',
      url='http://github.com/reuteran/reuter_util',
      author='Andreas Reuter',
      author_email='andreas.reuter@fu-berlin.de',
      license='MIT',
      packages=['reuter_util'],
      zip_safe=False, install_requires=['pandas', 'requests'])
