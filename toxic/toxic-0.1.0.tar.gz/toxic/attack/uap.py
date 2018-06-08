from __future__ import absolute_import, division, print_function

import numpy as np
from toxic.attack import Attack
from toxic.attack import DeepFool


class UAP(Attack):
    """
    Universal adversarial perturbations
    Reference:
        Universal adversarial perturbations,
        Moosavi-Dezfooli et al., https://arxiv.org/abs/1610.08401
    """
    def __init__(self, model, delta=0.2, max_iter=None, xi=10, ord=np.inf,
                 n_candidates=10, overshoot=0.02, max_iter_df=10):
        super(UAP, self).__init__()
        if not isinstance(model, nn.Module):
            raise ValueError('model must be an instance of nn.Module')
        self.model = model
        self.delta = delta
        self.n_candidates = n_candidates
        self.overshoot = overshoot
        self.max_iter = max_iter
        self.clip_min = clip_min
        self.clip_max = clip_max
        self.attack = DeepFool(model, n_candidates, overshoot,
                               max_iter=max_iter_df)

    def proj_lp(self, v, xi, p):
        # Project on the lp ball centered at 0 and of radius xi
        # SUPPORTS only p = 2 and p = Inf for now
        if p == 2:
            v = v * min(1, xi / np.linalg.norm(v.flatten(1)))
            # v = v / np.linalg.norm(v.flatten(1)) * xi
        elif p == np.inf:
            v = np.sign(v) * np.minimum(abs(v), xi)
        else:
             raise ValueError('Values of p different from 2 and Inf are currently not supported...')
        return v

    def generate(self, x):

        v = 0
        fooling_rate = 0.0
        n_images = x.size(0)

        i = 0
        while fooling_rate < 1 - delta and i < self.max_iter:
            # ompute the perturbation increments sequentially
            for k in range(n_images):
                cur_img = x[k:(k+1), :, :, :]
                f = self.model(x)
                _, y = torch.max(f, 1)
                f_adv = self.model(x + v)
                _, y_adv = torch.max(f_adv, 1)

                if int(y) == int(y_adv):
                    # Compute adversarial perturbation
                    adv_x, perturbation = self.deepfool(x + v)
                    v = v + perturbation

                    # Project on l_p ball
                    v = self.project_lp(v, xi, p)

            # add perturbation to x
            adv_x = x + v

            pred_orig = torch.zeros([n_images])
            pred_pert = torch.zeros([n_images])

            batch_size = 100.0
            n_batches = int(np.ceil(n_images / batch_size))

            # Compute the estimated labels in batches
            for b in range(n_batches):
                m = (b * batch_size)
                M = min((b + 1) * batch_size, n_images)
                f = self.model(x[m:M, ...])
                f_adv = self.model(adv_x[m:M, ...])

                _, y = torch.max(f, 1)
                _, y_adv = torch.max(f_adv, 1)
                pred_orig[m:M] = y
                pred_pert[m:M] = y_adv

            # Compute the fooling rate
            fooling_rate = torch.sum(pred_pert != pred_orig) / n_images
            i = i + 1

        return v
