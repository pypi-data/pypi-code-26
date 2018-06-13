from setuptools import setup, find_packages
import re

# Read version from __init__.py
with open('loadTDT/__init__.py', 'r') as file:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        file.read(), re.MULTILINE).group(1)

setup(name         = 'loadTDT',
      version      = version,
      description  = 'Read a TDT tank into a python dictionary',
      url          = 'https://github.com/logangrado/loadTDT',
      author       = 'Logan Grado',
      author_email = 'grado@umn.edu',
      license      = 'GNU GPLv3',
      packages     = ['loadTDT'],
      zip_safe     = False,
      install_requires = [
          'numpy'
      ])
