from distutils.core import setup
import os

VERSION=os.environ.get('CONAN_TOOLS_VERSION', '0.0.14')

setup(
  name = 'manu343726-conan-tools',
  packages = ['manu343726_conan_tools'],
  version = VERSION,
  description = 'Miscellaneous tools for development of conan.io recipes',
  author = 'Manu Sanchez',
  author_email = 'Manu343726@gmail.com',
  url = 'https://gitlab.com/Manu343726/conan-tools',
  download_url = 'https://gitlab.com/Manu343726/conan-tools/-/archive/v{version}/conan-tools-v{version}.tar.gz'.format(version=VERSION),
  keywords = ['conan'],
  classifiers = [],
  entry_points={
    'console_scripts': [
        'manu343726-conan-tools=manu343726_conan_tools.main:main'
    ]
  }
)
