from __future__ import absolute_import, division, print_function

import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable
from toxic.shim import is_volatile

# Tensor Related Functions


def to_gpu(x, *args, **kwargs):
    r""" Moves torch tensor to gpu if CUDA is available.
    Args:
        x (torch.Tensor): tensor to be moved to the GPU.
    Returns:
        torch.Tensor: Tensor moved to the GPU if CUDA is available otherwise the
                      original tensor.
    """
    return x.cuda(*args, **kwargs) if torch.cuda.is_available() else x


def get_layer(model, idx):
    """ Returns the layer of the corresponding index of the model."""
    return list(model.children())[idx]


def cut_model(model, idx):
    """ Makes a new model with the layers extracted from the input model. """
    nets = list(model.children())[:-idx]
    return TruncatedModel(nets)


class TruncatedModel(nn.Module):
    def __init__(self, parts):
        """parts is a list of nn.Module components"""
        super(TruncatedModel, self).__init__()
        self.features = nn.Sequential(*parts)

    def forward(self, x):
        x = self.features(x)
        return x
