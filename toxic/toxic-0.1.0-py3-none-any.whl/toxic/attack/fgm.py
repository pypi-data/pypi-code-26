from __future__ import absolute_import, division, print_function

import numpy as np
import torch
from torch.autograd import Variable
from toxic.attack import Attack
from toxic.attack.functional import fgm, fgsm


class FGM(Attack):
    """
    Fast Gradient Method. It extends the original implementation with
    additional options of L1, L2, and L-inf norms (sign).
    Reference:
        Explaining and Harnessing Adversarial Examples,
        Goodfellow et al., CoRR2014, https://arxiv.org/abs/1412.6572
    """
    def __init__(self, model, eps=0.3, ord=np.inf,
                 clip_min=None, clip_max=None, apply_softmax=False):
        super(FGM, self).__init__(model)
        if not isinstance(model, nn.Module):
            raise ValueError('model must be an instance of nn.Module')
        self.model = model
        self.eps = eps
        self.ord = ord
        self.clip_min = clip_min
        self.clip_max = clip_max
        self.targeted = False
        self.apply_softmax = apply_softmax

    def generate(self, x, y=None, target=None):
        pred = self.model(x)
        if self.apply_softmax:
            pred = F.softmax(pred, dim=1)

        if target is not None:
            y = target
            self.targeted=True
        elif y is not None:
            y = y
            self.targeted = False
        else:
            _, y = torch.max(pred, 1)
            y = Variable(y.data)

        return fgm(x, pred, y=y, eps=self.eps, ord=self.ord,
                   clip_min=self.clip_min, clip_max=self.clip_max,
                   targeted=self.targeted)


class FGSM(Attack):
    """
    Fast Gradient Sign Method.
    Reference:
        Explaining and Harnessing Adversarial Examples,
        Goodfellow et al., CoRR2014, https://arxiv.org/abs/1412.6572
    """
    def __init__(self, model, eps=0.3, ord=np.inf,
                 clip_min=None, clip_max=None, apply_softmax=False):
        super(FGSM, self).__init__()
        self.model = model
        self.eps = eps
        self.ord = ord
        self.clip_min = clip_min
        self.clip_max = clip_max
        self.apply_softmax = apply_softmax

    def generate(self, x):
        pred = self.model(x)
        if self.apply_softmax:
            pred = F.softmax(pred, dim=1)

        return fgsm(x, pred, eps=self.eps, ord=self.ord,
                    clip_min=self.clip_min, clip_max=self.clip_max)
