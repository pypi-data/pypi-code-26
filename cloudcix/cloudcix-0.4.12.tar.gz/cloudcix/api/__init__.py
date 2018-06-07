"""
Wrapper around the python requests module for ease of interaction with all
CloudCIX services

Basic usage: ``cloudcix.api.<application>.<service>.<method>``

More detailed usage information will be available under each of the above terms

To see even more details about the API you can visit our
`HTTP API Reference <https://docs.cloudcix.com/>`_

To see more information about the various methods (list, read, etc.), see the
:doc:`client_reference` page

For examples of a call for each of these methods, see the :doc:`examples` page

.. warning:: Some applications and/or services are private and can only be used
  by Users in the CloudCIX Member.

  These are still documented here but will be marked clearly

.. note:: Any service that implements the ``update`` method also implements the
  ``partial_update`` method, which does the same thing without needing to pass
  a full representation of the object, only the fields that need updating
"""

from .app_manager import app_manager
from .asset import asset
from .circuit import circuit
from .contacts import contacts
from .documentation import documentation
from .financial import financial
from .helpdesk import helpdesk
from .iaas import iaas
from .membership import membership
from .reporting import reporting
from .repository import repository
from .scheduler import scheduler
from .scm import scm
from .security import security
from .training import training
