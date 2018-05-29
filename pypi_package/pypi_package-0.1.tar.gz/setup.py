from distutils.core import setup
setup(
  name = 'pypi_package',
  packages = ['pypi_package'], # this must be the same as the name above
  version = '0.1',
  description = 'This package only records what cato y perro love story',
  author = 'Emrys-Hong',
  author_email = 'hongpengfei.emrys@gmail.com',
  url = 'https://github.com/Emrys-Hong/pypi_package', # use the URL to the github repo
  download_url = 'https://github.com/Emrys-Hong/pypi_package/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['testing', 'logging', 'example'], # arbitrary keywords
  classifiers = [],
)
