"""
Module for generating displaced structures

TODO
----
Add harmonic phonon eigenmode displacement method
"""

from .rattle import (generate_mc_rattled_structures,
                     generate_rattled_structures)

__all__ = ['generate_mc_rattled_structures', 'generate_rattled_structures']
