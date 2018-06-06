__version__ = '3.0.1'

import sys

from .magic import Lookup
from .decorator import LookupDecorator as lookup
from .package import AbstractPackage
from .token import AbstractToken

try:
    from ats.cisco.stats import CesMonitor
    CesMonitor(action = 'abstract', application='Genie').post()
except Exception:
    try:
        from ats.utils.stats import CesMonitor
        CesMonitor(action = 'abstract', application='Genie').post()
    except Exception:
        pass

__all__ = ['Lookup', 'LookupDecorator']

def declare_package(name):
    '''declare_package

    declare an abstraction package. This api should be called at the top of your
    abstraction package's __init__.py file. 
    
    Argument
    --------
        name (str): module fully qualified name (eg, __name__)

    Example
    -------
        >>> from genie import abstract
        >>> abstract.declare_package(__name__)
    '''

    try:
        # get the module object
        module = sys.modules[name]

    except KeyError:

        # module not loaded/non-existent.
        raise ValueError("'%s' is not a valid module." % name)

    # instanciate the abstraction package
    # (always delay to avoid circular reference due to recursive import)
    module.__abstract_pkg = AbstractPackage(name, delay = True)



def declare_token(name):
    '''declare_token

    declare an abstraction token. This api should be called at the top of your
    abstraction token module's __init__.py file. 
    
    Argument
    --------
        name (str): module fully qualified name (eg, __name__)

    Example
    -------
        >>> from genie import abstract
        >>> abstract.declare_token(__name__)
    '''
    
    try:
        # get the module object
        module = sys.modules[name]

    except KeyError:

        # module not loaded/non-existent.
        raise ValueError("'%s' is not a valid module." % name)

    # mark it as an abstraction token
    module.__abstract_token = AbstractToken(name)


