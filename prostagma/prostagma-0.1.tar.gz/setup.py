from distutils.core import setup
from setuptools import setup, find_packages

def check_dependencies():
    install_requires = []
    
    try:
        import numpy
    except ImportError:
        install_requires.append('numpy')
    try:
        import scipy
    except ImportError:
        install_requires.append('scipy')
    try:
        import sklearn
    except ImportError:
        install_requires.append('scikit-learn')
    try:
        import pandas
    except ImportError:
        install_requires.append('pandas')
    try:
        import keras
    except ImportError:
        install_requires.append('keras')
    return install_requires

install_requires = check_dependencies()

setup(
  name = 'prostagma',
  version = '0.1',
  description = 'Hyperparameters Tuning Library',
  author = 'Skopos-team',
  packages=find_packages(),
  install_requires=install_requires,
  author_email = 'skopos.library@gmail.com',
  url = 'https://github.com/Skopos-team/Prostagma', 
  license='Apache2',
  download_url = 'https://github.com/Skopos-team/Prostagma/archive/0.1.tar.gz',
  keywords = ['testing', 'logging', 'example'],
  classifiers = ['Programming Language :: Python :: 3.5',
                  'Operating System :: POSIX',
                  'Operating System :: Unix',
                  'Operating System :: MacOS'
                  ],
)