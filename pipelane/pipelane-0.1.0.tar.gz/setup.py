from setuptools import find_packages, setup

with open('pipelane/__init__.py', 'r') as f:
  for line in f:
    if line.startswith('__version__'):
      version = line.strip().split('=')[1].strip(' \'"')
      break
  else:
    version = '0.0.1'

with open('README.md', 'r') as f:
  long_description = f.read()

requirments = [
  'osascript>=1.0.2'
]

setup(
  name = 'pipelane',
  version = version,
  description = 'A small pipelane package',
  long_description = long_description,
  author = 'Richard Li',
  author_email = 'lifuzu+pipelane@gmail.com',
  long_description_content_type = 'text/markdown',
  url = 'https://github.com/lifuzu/pipelane',

  keywords = [
    'cli',
    'pipelane',
    'build system',
  ],

  classifiers = (
    'Programming Language :: Python :: 2.7',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
  ),

  install_requires = requirments,
  tests_require = [],

  packages = find_packages(),
  entry_points = {
    'console_scripts': [
      'pipelane = pipelane.cli:main',
    ],
  }
)
