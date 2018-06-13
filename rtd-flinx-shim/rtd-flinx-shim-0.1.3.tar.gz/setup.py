# -*- coding: utf-8 -*-
from distutils.core import setup

install_requires = \
['flinx>=0.1.1,<0.2.0']

entry_points = \
{'console_scripts': ['rtd-flynx = rtd_flinx_shim:cli',
                     'sphinx-build = rtd_flinx_shim:cli']}

setup_kwargs = {
    'name': 'rtd-flinx-shim',
    'version': '0.1.3',
    'description': 'Trick Read the Docs into running Flinx.',
    'long_description': "RTD Flinx Shim\n==============\n\nTrick `Read the Docs`_ into using `Flinx`_.\n\nYou don't want this package on your development machine. The `Flinx`_\ndocumentation describes the single, very specific, use case for this package.\n\n.. _Read the Docs: https://readthedocs.org\n.. _Flinx: https://github.com/osteele/flinx\n\nLicense\n-------\n\nMIT\n",
    'author': 'Oliver Steele',
    'author_email': 'steele@osteele.com',
    'url': 'https://github.com/osteele/rtd-flinx-shim',
    'py_modules': 'rtd_flinx_shim',
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.0',
}


setup(**setup_kwargs)
