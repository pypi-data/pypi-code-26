from __future__ import absolute_import, division, print_function

import numpy as np
import torch
from torch.autograd import Variable, grad
from toxic.attack import Attack
from toxic.util import clip_eta


class FeatureAdversaries(Attack):
    """
    Produces adversarial image based on internal layers of network
    representations.
    tags - white box, targeted, iterative, image specific
    Reference:
        Adversarial Manipulation of Deep Representations,
        Sabour et al., https://arxiv.org/abs/1511.05122
    """
    def __init__(self, model, layer, eps=0.3, eps_iter=0.5, ord=np.inf, n_iter=10,
                 clip_min=None, clip_max=None, **kwargs):
        """
        Args:
            model (nn.Module): must return the output and layer output
            layer (int): index of the layer to attack
        """
        super(FeatureAdversaries, self).__init__()
        if not isinstance(model, nn.Module):
            raise ValueError('model must be an instance of nn.Module')
        self.model = model
        self.layer = layer
        self.eps = eps
        self.eps_iter = eps_iter
        self.ord = ord
        self.n_iter = n_iter
        self.clip_min = clip_min
        self.clip_max = clip_max

    def generate(self, x, g):
        """
        x: source
        g: guide
        """
        eta = torch.randn(x.size())
        eta = clip_eta(eta, self.ord, self.eps)

        _, g_feat = self.model(g)

        # run iterations
        for i in range(self.n_iter):
            eta = self._step(x, eta, g_feat)

        adv_x = x + eta
        # clip by the range [clip_min, clip_max]
        if (self.clip_min is not None) and (self.clip_max is not None):
            adv_x = torch.clamp(adv_x, self.clip_min, self.clip_max)
        return adv_x

    def _step(self, x, eta, g_feat):
        """
        Args:
            x (Variable): Input variable
            eta (Variable): Perturbation tensor with the same shape of x
            g_feat (Variable): internal tensor for guide
        """
        adv_x = Variable(x.data + eta, requires_grad=True)
        _, a_feat = self.model(adv_x)

        # negative for targeted attack
        loss = -torch.sum((a_feat - g_feat)**2))

        # gradient wrt adv_x & multiply with epsilon
        gradient = grad(loss, adv_x)[0]
        scaled_grad = self.eps_iter * torch.sign(gradient)

        adv_x = adv_x + scaled_grad
        if (self.clip_min is not None) and (self.clip_max is not None):
            adv_x = torch.clamp(adv_x, self.clip_min, self.clip_max)

        # repackage
        adv_x = Variable(adv_x.data)
        eta = adv_x - x
        eta = clip_eta(eta, self.ord, self.eps)

        return eta
