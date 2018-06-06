#-- powertools.__init__

"""--- powertools
    with additional batteries
"""

#----------------------------------------------------------------------------------------------#

# todo: metaclass that allows composition of classes using the | operator

from .setup.arguments import __version__

from .export import export              # decorator

from .std import name, qualname         # functions

from .struct import GreedyOrderedSet    # data structure

from .meta import classproperty         # wrapper decorator
from .meta import composable            # wrapper decorator
from .meta import assertion             # context manager

from .logging import AutoLogger         # module utility class

#----------------------------------------------------------------------------------------------#
