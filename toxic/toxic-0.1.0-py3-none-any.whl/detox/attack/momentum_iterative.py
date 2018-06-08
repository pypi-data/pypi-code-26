from __future__ import absolute_import, division, print_function

import torch
from torch.autograd import Variable, grad
import numpy as np
import torch.nn.functional as F
from toxic.attack import Attack
from toxic.util import clip_eta


class MomentumIterative(Attack):
    """
    Momentum Iterative Method integrates the momentum term into the iterative
    process for attacks. Momentum stabilizes the update directions and escape
    from poor local maxima during the iterations, resulting in more
    transferable adversarial examples.
    Reference:
        Boosting Adversarial Attacks with Momentum,
        Dong et al., https://arxiv.org/pdf/1710.06081.pdf
    """
    def __init__(self, model, eps=0.3, ord=np.inf, n_iter=10, lr=0.05,
                 decay_factor=1.0, clip_min=None, clip_max=None,
                 apply_softmax=False):
        super(MomentumIterative, self).__init__()
        if not isinstance(model, nn.Module):
            raise ValueError('model must be an instance of nn.Module')
        self.model = model
        self.n_iter = n_iter
        self.eps = eps
        self.ord = ord
        self.lr = lr
        self.decay_factor = decay_factor
        self.clip_min = clip_min
        self.clip_max = clip_max
        self.apply_softmax = apply_softmax
        self.targeted = False

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

        # initialize
        momentum = 0
        adv_x = Variable(x.data, requires_grad=True)

        # let's cook the perturbation
        for i in range(self.n_iter):
            pred = self.model(adv_x)
            if self.apply_softmax:
                pred = F.softmax(pred, dim=1)

            loss = F.cross_entropy(pred, y, size_average=False)
            if self.targeted:
                loss = -loss
            # get gradients wrt x
            gradient = grad(loss, adv_x)[0]

            # normalize gradient and add to accumulated gradient
            gradient /= (1e-12 + torch.mean(torch.abs(gradient)))

            momentum = self.decay_factor * momentum + gradient
            if self.ord == np.inf:  # L-inf (sign)
                norm_grad = torch.sign(momentum)
            else:  # Lp normalization
                norm_grad = F.normalize(momentum, self.ord)
            scaled_grad = self.lr * norm_grad
            adv_x = adv_x + scaled_grad
            adv_x = x + clip_eta(adv_x - x, self.ord, self.eps)

            # clip if necessary
            if (self.clip_min is not None) and (self.clip_max is not None):
                adv_x = torch.clamp(adv_x, self.clip_min, self.clip_max)
            adv_x = Variable(adv_x.data, requires_grad=True)  # stop gradient

        return adv_x
