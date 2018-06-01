import setuptools

with open('README.md', 'r') as fh:
  long_description = fh.read()

setuptools.setup(
  name = 'myml',
  packages = setuptools.find_packages(),
  version = '0.0.2',
  description = 'Test implementations of Machine Learning algorithms.',
  long_description = long_description,
  author = 'Brett Clark',
  author_email = 'clarkbab@gmail.com',
  url = 'https://github.com/clarkbab/myml',
  download_url = 'https://github.com/clarkbab/myml/archive/0.0.1.tar.gz',
  keywords = ['machine learning'],
  classifiers = []
)
