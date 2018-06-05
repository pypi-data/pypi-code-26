from .cluster_space import ClusterSpace
from .structure_container import StructureContainer
from .force_constant_potential import ForceConstantPotential
from .force_constants import ForceConstants
from .core.core_config import core_config


"""
hiPhive module.
"""

__project__ = 'hiPhive'
__description__ = 'High-order force constants for the masses'
__authors__ = ['Fredrik Eriksson',
               'Erik Fransson',
               'Paul Erhart']
__copyright__ = '2018'
__license__ = 'MIT'
__credits__ = ['Fredrik Eriksson',
               'Erik Fransson',
               'Paul Erhart']
__version__ = '0.2'
__all__ = ['ClusterSpace',
           'StructureContainer',
           'ForceConstantPotential',
           'ForceConstants',
           'core_config']
__maintainer__ = 'The hiPhive developers team'
__maintainer_email__ = 'hiphive@materialsmodeling.org'
__status__ = 'beta-version'
__url__ = 'http://hiphive.materialsmodeling.org/'
