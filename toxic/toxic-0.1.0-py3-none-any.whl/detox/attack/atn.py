from __future__ import absolute_import, division, print_function

import torch
import torch.nn as nn
from torch.nn import functional as F
from torch.autograd import Variable
from torch.optim import Adam
from ignite.trainer import Trainer

from toxic.attack import Attack
from toxic.nn import autoencoder


class ATN(Attack):
    """
    Adversarial Transformation Networks
    Reference:
        Adversarial Transformation Networks:
        Learning to Generate Adversarial Examples,
        Baluja et al., https://arxiv.org/abs/1703.09387
    """
    def __init__(self, model, adv_model=None, alpha=1.5, beta=0.1):
        super(ATN, self).__init__(model)
        if not isinstance(model, nn.Module):
            raise ValueError('model must be an instance of nn.Module')
        self.model = model

        if adv_model is None:
            adv_model = autoencoder(pretrained=True)
        else:
            if not isinstance(adv_model, nn.Module):
                raise ValueError('Model must be an instance of nn.Module')
        self.adv_model = adv_model
        self.alpha = alpha
        self.beta = beta

    def criterion(self, x, adv_x, pred, rerank):
        Lx = torch.sum(
            torch.sqrt(torch.sum((adv_x - x)**2 + 1e-12, 1))
        )
        Ly = torch.sum(
            torch.sqrt(torch.sum((pred - rerank)**2 + 1e-12, 1))
        )
        return self.beta * Lx + Ly

    def rerank(self, probs, target):
        """ Reranking function that modifies y such that y_k < y_t.
        we use reranking function that maintains the rank order of all but the
        targeted class in order to minimize distortions"""
        max_val, _ = torch.max(probs, 1)
        probs[:, target] = max_val
        reranked = F.normalize(probs)
        return reranked

    def trainer(self, target, optimizer, cuda=False):

        def _prepare_batch(batch, volatile=False):
            x, y = batch
            if cuda:
                x, y = x.cuda(), y.cuda()
            return (Variable(x, volatile=volatile),
                    Variable(y, volatile=volatile))

        def _update(batch):
            self.adv_model.train()
            self.model.eval()
            optimizer.zero_grad()

            x, y = _prepare_batch(batch)
            adv_x = self.adv_model(x)
            logits = self.model(x)
            probs = F.softmax(logits, dim=1)
            probs = Variable(probs.data)

            reranked = self.rerank(probs, target)
            reranked = Variable(reranked.data)

            loss = self.criterion(x, adv_x, probs, reranked)
            loss.backward()
            optimizer.step()
            return loss.data[0]

        trainer = Trainer(_update)
        return trainer

    def generate(self, x):
        adv_x = self.adv_model(x)
        return adv_x, None
