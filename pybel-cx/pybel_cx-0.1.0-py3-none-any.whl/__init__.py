# -*- coding: utf-8 -*-

"""A PyBEL extension for interconversion with CX.

Requirements
------------
To support this feature, we need 2 command line scripts:

1. Export script: takes a CX document from STDIN stream and write a BEL network out to STDOUT. Writes error message to STDERR when error occurs.
2. Import script: takes a BEL network from STDIN and write a CX network to STDOUT

Here are some other specs for these scripts:

- Relatively easy to deploy.
- Have minimum memory footprint possible.
- The scripts will be run as a task from the server so it is OK if runtime is long.
- They can take extra command line arguments if necessary
- The scripts return 0 when succeeded and returns a non-zero exit code when it failed.

Installation
------------
Before this is deployed to PyPI, it can be installed with:

.. code-block:: sh

   $ python3 -m pip install git+https://github.com/pybel/pybel-cx.git

Command Line Usage
------------------
PyBEL-CX installs two command line utilities: ``bel_to_cx`` and ``cx_to_bel``.

CX to BEL
~~~~~~~~~
Running this script has the caveat that the CX document should conform to the schema created by PyBEL-CX.

.. code-block:: sh

   $ cat my_network.cx | cx_to_bel > my_network.bel

BEL to CX
~~~~~~~~~
.. code-block:: sh

   $ cat my_network.bel | bel_to_cx > my_network.cx

"""

from .cx import from_cx, from_cx_file, from_cx_jsons, to_cx, to_cx_file, to_cx_jsons
from .ndex_utils import from_ndex, to_ndex

__all__ = [
    'from_cx',
    'from_cx_file',
    'from_cx_jsons',
    'to_cx',
    'to_cx_file',
    'to_cx_jsons',
    'from_ndex',
    'to_ndex',
]

__version__ = '0.1.0'

__title__ = 'pybel_cx'
__description__ = 'A PyBEL extension for interconversion with CX'
__url__ = 'https://github.com/pybel/pybel-cx'

__author__ = 'Charles Tapley Hoyt'
__email__ = 'charles.hoyt@scai.fraunhofer.de'

__license__ = 'MIT License'
__copyright__ = 'Copyright (c) 2018 Charles Tapley Hoyt'
