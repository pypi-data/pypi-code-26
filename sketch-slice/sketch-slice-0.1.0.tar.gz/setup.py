# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['sketch_slice']

package_data = \
{'': ['*']}

install_requires = \
['click>=6.7.0.0,<7.0.0.0',
 'envoy>=0.0.3.0,<0.0.4.0',
 'glom>=18.1.0.0,<19.0.0.0',
 'jsonpath-ng>=1.4.0.0,<2.0.0.0',
 'toolz>=0.9.0.0,<0.10.0.0']

entry_points = \
{'console_scripts': ['sketch-slice = sketch_slice.cli:main']}

setup_kwargs = {
    'name': 'sketch-slice',
    'version': '0.1.0',
    'description': 'Slice sketch files for React Native import.',
    'long_description': None,
    'author': 'Dotan Nahum',
    'author_email': 'jondotan@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
}


setup(**setup_kwargs)
