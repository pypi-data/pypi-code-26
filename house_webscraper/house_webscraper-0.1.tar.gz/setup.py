#from distutils.core import setup
from  setuptools import setup
long_description = """A class for scraping data and data anylytics from house properties sites

The package is intended for use by data analysts/scientists who require easy access to download property listing data in nicely formatted Pandas DataFrames ready for analysis.
"""

setup(
    name = 'house_webscraper',
    packages = ['house_webscraper'], # Must be same as name
    version = '0.1',
    description = 'A class for scraping data from various house properties sites ',
    long_description = long_description,
    author = 'Elias Altrabsheh and Ben Busby',
    author_email = 'elias.altrabsheh@gmail.com',
    url = 'https://github.com/EliasCode2015/House-Price-Prediction-Model',
    # This specifies which other Pip packages your package
    # requires to be installed:
    install_requires = [
      'pandas',
      'requests',
      'lxml'
    ],
    keywords = ['webscraping', 'rightmove', 'data'],
    license='MIT',
    classifiers=[
      # For full list of relevant classifiers, see:
      # https://pypi.python.org/pypi?%3Aaction=list_classifiers

      # How mature is this project?
      'Development Status :: 4 - Beta',

      # Who is the project intended for?
      'Intended Audience :: End Users/Desktop',

      # Pick license (should match "license" above)
      'License :: OSI Approved :: MIT License',

      # Specify Python versions supported. In particular, ensure
      # to indicate whether you support Python 2, Python 3 or both.
      'Programming Language :: Python :: 3.6',
    ],
)
