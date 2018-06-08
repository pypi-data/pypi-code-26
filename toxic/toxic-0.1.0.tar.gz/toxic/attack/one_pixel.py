from __future__ import absolute_import, division, print_function

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from toxic.attack import Attack


class OnePixel(Attack):
    """
    One-Pixel Attack is a semi-blackbox Attack which only requires the
    probability output of the model. Rather than having a constraint on the
    intensity of the perturbation, it considers the number of pixels as the
    limitation.
    Reference:
        One pixel attack for fooling deep neural networks,
        Su et al., https://arxiv.org/abs/1710.08864
    """
    def __init__(self, model, F=0.5, C=0.5, n_iter=75, apply_softmax=False):
        super(OnePixel, self).__init__()
        if not isinstance(model, nn.Module):
            raise ValueError('model must be an instance of nn.Module')
        self.model = model
        self.targeted
        self.F = F
        self.C = C
        self.n_iter = n_iter
        self.apply_softmax = apply_softmax

    def generate(self, x, y=None, target=None):
        """
        iteration of mutation, crossover and selection
        """
        pred = self.model(x)
        if self.apply_softmax:
            pred = F.softmax(pred, dim=1)

        if target is not None:
            y = target
            self.targeted = True
        elif y is not None:
            y = y
            self.targeted = False
        else:
            _, y = torch.max(pred, 1)
            y = Variable(y.data)

        batch_size, C, H, W = x.size()
        flatten = x.view(batch_size, -1)
        #
        # for b in range(batch_size):
        #     flat_img  = x[b]
        #     fitness = list(map(objective, flat_img))
        #
        #     for i in range(max_iter):
        #         mutants = mutate(pop, fitness, F)
        #         trial = crossover(pop, mutants, C)
        #         pop, fitness = select(objective, pop, fitness, trial)
        #         print(pop)

    def objective(self):
        return 1

    def random_unique(self, length, count, include=[], exclude=[]):
        indices = list(include)
        while len(indices) < count:
            next = np.random.randint(length)
            while next in indices or next in exclude:
                next = np.random.randint(length)
            indices.append(next)
        return indices

    def mutate(self, pop, fitness, F):
        pop = np.array(pop, copy=False)
        fitness = np.array(fitness, copy=False)
        pop_size = len(pop)
        de_idx = lambda count: np.array(
            [random_unique(pop_size, count, exclude=[i])
             for i in range(pop_size)]
        )

        # Could be more methods... but
        parents = pop[de_idx(3)]
        return parents[:,0] + F * (parents[:,1] - parents[:,2])

    def crossover(self, pop, mutant, C):
        # mutant enters the trial victor with probability C
        pop = np.array(pop, copy=False)
        mask = np.random.random_sample(mutant.shape) < C
        return np.where(mask, mutant, pop)

    def select(self, objective, pop, fitness, trial, stochastic=False):
        """
            objective: function
            pop: original population
            fitness: original population fitness
            trial_pop: trial population
        """
        pop = np.array(pop, copy=False)
        fitness = np.array(fitness, copy=False)

        # objective function is evaluated for each trial vector
        trial_fitness = np.array(list(map(objective, trial)))

        # storn-price selection method
        mask = fitness < trial_fitness
        new_fitness = np.where(mask, fitness, trial_fitness)
        new_pop = np.where(mask, pop, trial)
        if stochastic:
            new_fitness = np.array(list(map(objective, new_pop)))
        return new_pop, new_fitness
