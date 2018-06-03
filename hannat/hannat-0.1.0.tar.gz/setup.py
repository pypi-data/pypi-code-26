# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['hannat']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'hannat',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Nyanye',
    'author_email': 'iam@nyanye.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*',
}


setup(**setup_kwargs)
