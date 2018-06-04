from setuptools import setup
from setuptools import find_packages

desc = """\
SMS-cli
==============

Command line interface for sending AT (ATtention) commands via serial port to GSM shield module.
"""

setup(name="sms-cli",
      version="1.0.0",
      author="luka",
      author_email="lukamatosevic5@gmail.com",
      url='https://github.com/Lujo5/sms-cli',
      download_url='https://github.com/Lujo5/sms-cli/archive/1.0.tar.gz',
      packages=find_packages(),
      install_requires=["pyserial", "argparse"],
      entry_points={
          'console_scripts': [
              'sms-cli = cli.main:main'
          ]
      },
      keywords=['sms', 'cli', 'messaging', 'gsm'],
      description="SMS command line interface tool",
      long_description=desc)
