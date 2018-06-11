# -*- coding: utf-8 -*-
from distutils.core import setup


setup_kwargs = {
    'name': 'aionursery',
    'version': '0.1.0',
    'description': 'Manage background asyncio tasks',
    'long_description': None,
    'author': 'Dmitry Malinovsky',
    'author_email': 'damalinov@gmail.com',
    'url': None,
    'py_modules': 'aionursery',
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
