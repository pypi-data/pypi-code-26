from __future__ import absolute_import, division, print_function

import logging

name = "toxic"
__version__ = '0.1.0'

# Default logger to prevent 'No handler found' warning.
logging.getLogger(__name__).addHandler(logging.NullHandler())

from toxic.functional import *
from toxic.metric import *

def set_seed(seed):
    """
    Sets seeds of torch, numpy, and torch.cuda (if available).
    :param int rng_seed: The seed value.
    """
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
