#!/usr/bin/env python
# setup.py generated by flit for tools that don't yet use PEP 517

from distutils.core import setup

packages = \
['nyptune', 'nyptune.directory', 'nyptune.handler']

package_data = \
{'': ['*']}

install_requires = \
['tqdm']

entry_points = \
{'console_scripts': ['nyptune = nyptune.cli:main']}

setup(name='nyptune',
      version='0.0.1.1527314894',
      description='Nyptune hides a copy of your environment in your Jypyter notebooks so that other people can easily reproduce your work',
      author='Kyle Maxwell',
      author_email='kyle@kylemaxwell.com',
      url='https://github.com/fizx/nyptune',
      packages=packages,
      package_data=package_data,
      install_requires=install_requires,
      entry_points=entry_points,
      python_requires='>=3.6',
     )
