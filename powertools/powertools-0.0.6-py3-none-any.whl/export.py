#-- powertools.export

'''
support for wildcard imports
'''

__all__ = ['export']

from inspect import currentframe
from inspect import getouterframes

#-------------------------------------------------------------------------------------------------#

def export( obj ) :
    ''' add obj to caller's module's global __all__ list, creating it if it doesn't exist yet
        the __all__ module-scope variable lists the names to be imported
            when another module writes `from caller_module import *`
    '''

    f_globals = getouterframes( currentframe( ) )[1].frame.f_globals
    if '__all__' not in f_globals:
        f_globals['__all__'] = list()
    try :
        f_globals['__all__'].append( obj.__name__ )
    except AttributeError :
        f_globals['__all__'].append( obj.__class__.__name__ )
    return obj

#-------------------------------------------------------------------------------------------------#
