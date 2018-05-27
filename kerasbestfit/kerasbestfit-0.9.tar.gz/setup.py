from setuptools import setup, find_packages
setup(
  name = 'kerasbestfit',
  packages = ['kerasbestfit'],
  version = '0.9',
  python_requires='>=3.0',
  install_requires=['keras',],
  description = 'For finding the best model using Keras.',
  author = 'Russ Beuker',
  author_email = 'russbeuker@gmail.com',
  url = 'https://github.com/russbeuker/kerasbestfit',
  keywords = ['keras', 'fit', 'best'],
  classifiers = [],
)