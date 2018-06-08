from __future__ import absolute_import, division, print_function

import torch as torch
from torch.nn import functional as F
from torch.autograd import Variable, grad
from torch.autograd.gradcheck import zero_gradients
from toxic.attack import Attack


class DeepFool(Attack):
    """
    DeepFool computes adversarial samples based on iterative linearization
    of the classifier.
    Reference:
        DeepFool: a simple and accurate method to fool deep neural networks,
        Moosavi-Dezfooli et al., https://arxiv.org/pdf/1511.04599.pdf
    """
    def __init__(self, model, n_candidates=10, overshoot=0.02, max_iter=50,
                 clip_min=None, clip_max=None):
        """
        Args:
            model: models must output the logits (activation before softmax).
            k: number of k candidate classes to be considered in the attack.
               Unless specified, the number is chosen according to the
               prediction confidence.
            overshoot: termination criterion
            max_iter: maximum number of iterations
        """
        super(DeepFool, self).__init__()
        if not isinstance(model, nn.Module):
            raise ValueError('model must be an instance of nn.Module')
        self.model = model
        self.n_candidates = n_candidates
        self.overshoot = overshoot
        self.max_iter = max_iter
        self.clip_min = clip_min
        self.clip_max = clip_max

    def generate(self, x):
        """
        x: BxHxWxC
        Returns perturbed image and the perturbation.
        """
        batch_size, C, H, W = x.size()
        adv_x = Variable(x.data, requires_grad=True)

        # record original prediction of the model
        logits = self.model(adv_x)
        f, idx = logits.sort()
        idx = idx.data
        k_0 = idx[:, 0]

        k_i = k_0
        i = 0
        r_tot = Variable(torch.zeros_like(x.data))
        while k_0.eq(k_i).any() and i < self.max_iter:

            # get gradients wrt adv_x
            grad_0 = grad(f[:, k_0], adv_x, retain_graph=True)[0]

            for b in range(batch_size):
                pert = None

                for k in range(1, self.n_candidates):
                    zero_gradients(adv_x)
                    # get gradients wrt adv_x
                    grad_k = grad(f[b, idx[b, k]], adv_x, retain_graph=True)[0]

                    w_k = grad_k - grad_0
                    f_k = f[b, idx[b, k]] - f[b, idx[b, 0]]

                    pert_k = (
                        torch.abs(f_k) /
                        torch.sum((F.normalize(w_k.view(1, -1), 2)) + 1e-12)
                    )

                    # determine which w_k to use
                    if pert is None or (pert_k < pert).any():
                        pert = pert_k
                        w = w_k

                r_i = (pert + 1e-12) * w / F.normalize(w, 2)
                r_tot[b, ...] = r_tot[b, ...] + r_i

            # add perturbation
            adv_x = adv_x + (1 + self.overshoot) * r_tot
            adv_x = Variable(adv_x.data, requires_grad=True)

            f = self.model(adv_x)
            _, k_i = torch.max(f, 1)
            k_i = k_i.data
            i += 1

        adv_x = (1 + self.overshoot) * r_tot + x
        # clip if necessary
        if (self.clip_min is not None) and (self.clip_max is not None):
            adv_x = torch.clamp(adv_x, self.clip_min, self.clip_max)
        return adv_x, r_tot
