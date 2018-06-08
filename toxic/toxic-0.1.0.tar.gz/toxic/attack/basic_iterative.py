from __future__ import absolute_import, division, print_function

import torch
from torch.autograd import Variable
from toxic.attack import Attack
import numpy as np
import torch.nn.functional as F
from toxic.attack.functional import fgm


class BasicIterative(Attack):
    """
    Basic Iterative Method (Kurakin et al. 2016).
    Reference:
        Adversarial Examples In The Phisical World,
        Kurakin et al., https://arxiv.org/abs/1607.02533
    """
    def __init__(self, model, eps=0.3, ord=np.inf, n_iter=1,
                 clip_min=None, clip_max=None, apply_softmax=False):
        super(BasicIterative, self).__init__()
        if not isinstance(model, nn.Module):
            raise ValueError('model must be an instance of nn.Module')
        self.model = model
        self.n_iter = n_iter
        self.eps = eps
        self.ord = ord
        self.clip_min = clip_min
        self.clip_max = clip_max
        self.targeted = False
        self.apply_softmax = apply_softmax

    def generate(self, x, y=None, target=None):

        if target is not None:
            y = target
            self.targeted = True
        elif y is not None:
            y = y
            self.targeted = False
        else:
            # optain label with the first prediction.
            pred = self.model(x)
            if self.apply_softmax:
                pred = F.softmax(pred, dim=1)
            _, y = torch.max(pred, 1)
            y = Variable(y.data)

        eta = Variable(torch.zeros_like(x.data))
        # let's cook the perturbation
        for i in range(self.n_iter):
            adv_x = Variable(x.data + eta.data, requires_grad=True)
            pred = self.model(adv_x)
            if self.apply_softmax:
                pred = F.softmax(pred, dim=1)

            eta = fgm(adv_x, pred, y=y, eps=self.eps, ord=self.ord,
                      clip_min=None, clip_max=None, targeted=self.targeted)
            eta = eta - x

            if self.ord == np.inf:
                norm = torch.clamp(eta, -self.eps, self.eps)
            else:
                norm = F.normalize(eta, self.ord)
            eta = eta * self.eps / (norm + 1e-12)
        # add perturbation
        adv_x = x + eta

        # clip if necessary
        if (self.clip_min is not None) and (self.clip_max is not None):
            adv_x = torch.clamp(adv_x, self.clip_min, self.clip_max)
        return adv_x
