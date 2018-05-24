# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['nummu']

package_data = \
{'': ['*']}

install_requires = \
['numpngw']

setup_kwargs = {
    'name': 'nummu',
    'version': '0.1.1',
    'description': 'An animated image maker.',
    'long_description': None,
    'author': 'Ju Lin',
    'author_email': 'soasme@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>= 3.6.0.0, < 4.0.0.0',
}


setup(**setup_kwargs)
