import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name='afb',
  version='0.1',
  author='Siu-Kei Muk (David)',
  author_email='muksiukei@gmail.com',
  description='A base for abstract factory in Python',
  long_description=long_description,
  long_description_content_type="text/markdown",
  url='https://github.com/dave-msk/afb',
  packages=setuptools.find_packages(),
  download_url='https://github.com/dave-msk/afb/archive/0.1.tar.gz',
  keywords=['afb', 'factory', 'abstract factory', 'config'],
  classifiers=[]
)
