from __future__ import absolute_import, division, print_function

import torch
from torch import optim
from torch.autograd import Variable
import numpy as np
from toxic.attack import Attack
from toxic.util import tanh_rescale, torch_arctanh, l2_dist


class CarliniWagnerL2(object):
    def __init__(self, confidence=0, lr=1e-3, init_const=1,
                 binary_search_steps=5, max_iter=1000, abort_early=True,
                 clip_min=-1, clip_max=1):
        self.confidence = confidence
        self.init_const = init_const
        self.lr = lr
        self.binary_search_steps = binary_search_steps
        self.repeat = binary_search_steps >= 10
        self.max_iter = max_iter
        self.abort_early = abort_early
        self.clip_min = clip_min
        self.clip_max = clip_max

    def _compare(self, output, target):
        if not isinstance(output, (float, int, np.int64)):
            output = np.copy(output)
            if self.targeted:
                output[target] -= self.confidence
            else:
                output[target] += self.confidence
            output = np.argmax(output)
        if self.targeted:
            return output == target
        else:
            return output != target

    def _criterion(self, output, target, dist, scale_const):
        # compute the probability of the label class versus the maximum other
        real = (target * output).sum(1)
        other = ((1. - target) * output - target * 10000.).max(1)[0]
        if self.targeted:
            # optimize for making the other class most likely
            loss1 = torch.clamp(other - real + self.confidence, min=0.)
        else:
            # optimize for making this class least likely.
            loss1 = torch.clamp(real - other + self.confidence, min=0.)
        loss1 = torch.sum(scale_const * loss1)
        loss2 = dist.sum()
        loss = loss1 + loss2
        return loss

    def _step(self, optimizer, x, eta, target, scale_const, orig):
        # create adv_x and convert to tanh space
        adv_x = x + eta
        adv_x = tanh_rescale(adv_x, self.clip_min, self.clip_max)

        output = self.model(adv_x)
        dist = l2_dist(adv_x, orig, keepdim=False)
        loss = self._criterion(output, target, dist, scale_const)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        return loss.data[0], dist, output, adv_x

    def generate(self, input, target, batch_idx=0):
        batch_size = input.size(0)

        # set the lower and upper bounds accordingly
        lower_bound = np.zeros(batch_size)
        scale_const = np.ones(batch_size) * self.initial_const
        upper_bound = np.ones(batch_size) * 1e10

        # placeholders for the best results
        o_best_l2 = [1e10] * batch_size
        o_best_score = [-1] * batch_size
        o_best_attack = torch.zeros_like(input)

        # convert to tanh space
        x = Variable(torch_arctanh(input), requires_grad=False)
        orig = tanh_rescale(x, self.clip_min, self.clip_max)

        # target variable TODO: efficient sparse computation
        target_onehot = torch.zeros(target.size() + (self.num_classes,))
        if self._cuda:
            target_onehot = target_onehot.cuda()
        target_onehot.scatter_(1, target.unsqueeze(1), 1.)
        target = Variable(target_onehot, requires_grad=False)

        # initialize noise
        eta = torch.zeros(x.size()).float()
        if self._cuda:
            eta = eta.cuda()
        eta = Variable(eta, requires_grad=True)

        optimizer = optim.Adam([eta], lr=self.lr)

        for search_step in range(self.binary_search_steps):
            best_l2 = [1e10] * batch_size
            best_score = [-1] * batch_size

            # The last iteration (if we run many steps) repeat the search once.
            if self.repeat and search_step == self.binary_search_steps - 1:
                scale_const = upper_bound

            scale_const_tensor = torch.from_numpy(scale_const).float()
            if self.cuda:
                scale_const_tensor = scale_const_tensor.cuda()
            scale_const_var = Variable(scale_const_tensor, requires_grad=False)

            prev_loss = 1e6
            for i in range(self.max_iter):
                # optimize the noise (eta)
                loss, dist, output, adv_x = self._step(
                    optimizer, x, eta, target, scale_const_var, orig)

                if self.abort_early and i % (self.max_steps // 10) == 0:
                    if loss > prev_loss * .9999:
                        print('Aborting early...')
                        break
                    prev_loss = loss

                # update the best result found so far TODO: recheck
                for b, (targ, out, l2) in enumerate(zip(target, output, dist)):
                    _, pred = torch.max(out)
                    if l2 < best_l2[b] and self._compare(pred, targ):
                        best_l2[b] = l2
                        best_score[b] = pred
                    if l2 < o_best_l2[b] and self._compare(pred, targ):
                        o_best_l2[b] = l2
                        o_best_score[b] = pred
                        o_best_attack[b] = adv_x[b]

            # adjust the constants
            for b in range(batch_size):
                if self._compare(best_score[b], target[b]) \
                   and best_score[b] != -1:
                    # success, divide const by two
                    upper_bound[b] = min(upper_bound[b], scale_const[b])
                    if upper_bound[b] < 1e9:
                        scale_const[b] = (lower_bound[b] + upper_bound[b]) / 2
                else:
                    # failure, either multiply by 10 if no solution found yet
                    #          or do binary search with the known upper bound
                    lower_bound[b] = max(lower_bound[b], scale_const[b])
                    if upper_bound[b] < 1e9:
                        scale_const[b] = (lower_bound[b] + upper_bound[b]) / 2
                    else:
                        scale_const[b] *= 10

        return o_best_attack
