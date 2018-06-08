from __future__ import absolute_import, division, print_function

from toxic.nn.autoencoder import Autoencoder, autoencoder
from toxic.nn.wgan import WGAN, wgan

__all__ = [
    # Classes
    'Autoencoder',
    'WGAN',
    # Functionals
    'autoencoder',
    'wgan',
]
