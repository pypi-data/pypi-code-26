from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
  name = 'featureflagclient',
  packages = ['featureflagclient'],
  version = '0.3',
  description = 'Service agnostic featureflag client',
  author = 'Tom Maslen',
  author_email = 'tom_maslen@hotmail.com',
  url = 'https://github.com/tmaslen/featureflagclient-python',
  download_url = 'https://github.com/tmaslen/featureflagclient-python/tarball/master',
  keywords = ['feature flag', 'feature toggle'],
)