# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['energyplus_wrapper', 'energyplus_wrapper.energyplus_wrapper']

package_data = \
{'': ['*'], 'energyplus_wrapper': ['energyplus_wrapper.egg-info/*']}

install_requires = \
['pandas>=0.23.0,<0.24.0', 'path.py>=11.0,<12.0']

setup_kwargs = {
    'name': 'energyplus-wrapper',
    'version': '0.6.0',
    'description': 'some usefull function to run e+ locally',
    'long_description': None,
    'author': 'Nicolas Cellier',
    'author_email': 'contact@nicolas-cellier.net',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
