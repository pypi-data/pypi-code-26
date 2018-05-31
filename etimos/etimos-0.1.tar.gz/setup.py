from distutils.core import setup
from setuptools import setup, find_packages

def check_dependencies():
    install_requires = []
    
    try:
        import numpy
    except ImportError:
        install_requires.append('seaborn')
    try:
        import pandas
    except ImportError:
        install_requires.append('pandas')

install_requires = check_dependencies()

setup(
  name = 'etimos',
  version = '0.1',
  description = 'Data Visualization Library',
  author = 'Skopos-team',
  packages=find_packages(),
  install_requires=install_requires,
  author_email = 'skopos.library@gmail.com',
  url = 'https://github.com/Skopos-team/Etimos', 
  license='Apache2',
  download_url = 'https://github.com/Skopos-team/Etimos/archive/0.1.tar.gz',
  keywords = ['testing', 'logging', 'example'],
  classifiers = ['Programming Language :: Python :: 3.5',
                  'Operating System :: POSIX',
                  'Operating System :: Unix',
                  'Operating System :: MacOS'
                  ],
)