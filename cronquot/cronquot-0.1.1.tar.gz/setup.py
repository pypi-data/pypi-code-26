"""Set up script"""
from setuptools import setup
import os


def _create_long_desc():
    """Create long description and README formatted with rst."""
    _long_desc = ''
    if os.path.isfile('README.md'):
        with open('README.md', 'r') as rf:
            return rf.read()
    if os.path.isfile('README.rst'):
        with open('README.rst', 'r') as rf:
            return rf.read()
long_desc = _create_long_desc()


# Setup
setup(name='cronquot',
      version='0.1.1',
      description='Cron scheduler.',
      long_description=long_desc,
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Libraries :: Python Modules'
          ],
      keywords='cron crontab schedule',
      author='Shohei Mukai',
      author_email='mukaishohei76@gmail.com',
      url='https://github.com/pyohei/cronquot',
      license='MIT',
      packages=['cronquot'],
      entry_points={
          'console_scripts': [
              'cronquot = cronquot.cronquot:execute_from_console'],
          },
      install_requires=['crontab'],
      test_suite='test' 
      )
