from __future__ import absolute_import, division, print_function

from toxic.attack import Attack
from toxic.attack.functional import saliency_map, jacobian
import numpy as np

class JSMA(Attack):
    r"""
    Jacobian-based Saliency Map Approach (JSMA). This method crafts adversarial
    samples based on an understanding of the mapping between inputs and outputs
    of DNNs.
    Reference:
        The Limitations of Deep Learning in Adversarial Settings,
        Papernot et al., https://arxiv.org/abs/1511.07528
    """
    def __init__(self, model, theta=1., gamma=0.1, clip_min=None, clip_max=None,
                 apply_softmax=False):
        super(JSMA, self).__init__()
        if not isinstance(model, nn.Module):
            raise ValueError('model must be an instance of nn.Module')
        self.model = model
        self.theta = theta
        self.gamma = gamma
        self.targeted = False
        self.clip_min = clip_min
        self.clip_max = clip_max
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
            prob = self.model(x)
            if self.apply_softmax:
                prob = F.softmax(prob, dim=1)
            _, y = torch.max(prob.data, 1)

        adv_x_batch = Variable(torch.zeros_like(x.data))
        for i in range(x.size(0)):
            adv_x = jsma(self.model, x[i], y[i], gamma=self.gamma,
                         apply_softmax=self.apply_softmax)
            adv_x_batch[i] = adv_x

        return adv_x_batch
