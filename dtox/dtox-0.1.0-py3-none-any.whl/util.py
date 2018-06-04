from __future__ import absolute_import, division, print_function

import math
import numpy as np
import torch
import torch.nn.functional as F


def l2_batch_norm(x, eps=1e-12):
    shape = x.size()
    x = x.view(shape[0], -1)
    x /= eps + torch.max(torch.abs(x), 1, keepdim=True)[0]
    square = torch.sum(torch.pow(x, 2), 0, keepdim=True)
    x_inv_norm = x / torch.rsqrt(math.sqrt(eps) + square)
    x_norm = x * x_inv_norm
    return x_norm.view(shape)


def kl_div(p, q):
    kl = torch.sum(p * (torch.log(p + 1e-12) - torch.log(q + 1e-12)), 1)
    return kl


def clip_eta(eta, ord, eps):
    if ord not in (np.inf, 1, 2):
        raise ValueError('ord must be one of np.inf, 1, 2')

    if ord == np.inf:
        norm = torch.clamp(eta, -eps, eps)
    else:
        norm = F.normalize(eta, ord)
    return eta * torch.clamp(eps / (norm + 1e-12), max=1.)


def tanh_rescale(x, min=-1., max=1.):
    return (torch.tanh(x) + 1) * 0.5 * (max - min) + min
