from __future__ import absolute_import, division, print_function

from toxic.attack import Attack


class BoundaryAttack(Attack):
    """
    TODO
    Reference:
        Decision-Based Adversarial Attacks: Reliable Attacks Against
        Black-Box Machine Learning Models
        Brendel et al., https://arxiv.org/abs/1712.04248
    """
    def __init__(self, model):
        super(BoundaryAttack, self).__init__()
        if not isinstance(model, nn.Module):
            raise ValueError('model must be an instance of nn.Module')
        self.model = model

    def generate(self, x):
        pass
