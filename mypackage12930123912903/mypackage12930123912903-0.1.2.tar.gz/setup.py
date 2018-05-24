# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mypackage12930123912903']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mypackage12930123912903',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>= 2.7.0.0, < 2.8.0.0',
}


setup(**setup_kwargs)
