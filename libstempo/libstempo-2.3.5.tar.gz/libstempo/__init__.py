from __future__ import absolute_import
__version__ = "2.3.5"

import os
if 'TEMPO2' not in os.environ:
    os.environ['TEMPO2'] = '/Users/vallis/anaconda3/share/tempo2'

from libstempo.libstempo import *
