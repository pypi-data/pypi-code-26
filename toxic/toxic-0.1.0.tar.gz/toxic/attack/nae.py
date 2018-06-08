from __future__ import absolute_import, division, print_function

import torch
import torch.nn as nn
from torch.nn import functional as F
from torch.autograd import Variable
from torch.optim import Adam
from ignite.trainer import Trainer

from toxic.attack import Attack
from toxic.nn import ae


class TextNAE(Attack):
    pass


class NAE(Attack):
    """
    Generates natural adversarial examples by searching in semantic space of
    dense and continuous data representation, which is learned by GAN.
    Reference:
        Generating Natural Adversarial Examples,
        Zhao et al., https://arxiv.org/abs/1710.11342
    """
    def __init__(self, model, G=None, D=None, inverter=None,
                 alpha=1.5, beta=0.1):
        super(NAE, self).__init__()

        if not isinstance(G, nn.Module):
            raise ValueError('model must be an instance of nn.Module')
        self.G = G
        if not isinstance(D, nn.Module):
            raise ValueError('model must be an instance of nn.Module')
        self.D = D

        if inverter is None:
            raise ValueError('inverter is not defined')
        elif generator is None:
            raise ValueError('generator is not defined')
        else:
            if not isinstance(inverter, nn.Module):
                raise ValueError('inverter must be an instance of nn.Module')
            if not isinstance(generator, nn.Module):
                raise ValueError('generator must be an instance of nn.Module')
        self.generator = generator
        self.inverter = inverter

        self.alpha = alpha
        self.beta = beta

    def grad_penalty(self, D, real, gen, context, lambd):
        alpha = torch.rand(real.size()).cuda()
        x_hat = alpha * real + ((1 - alpha) * gen).cuda()
        x_hat = Variable(x_hat, requires_grad=True)
        context = Variable(context)
        d_hat = D(x_hat, context)
        ones = torch.ones(d_hat.size()).cuda()
        gradients = grad(outputs=d_hat, inputs=x_hat,
                         grad_outputs=ones, create_graph=True,
                         retain_graph=True, only_inputs=True)[0]
        penalty = ((gradients.norm(2, dim=1) - 1) ** 2).mean() * lamb
        return penalty

    def criterion_g(self, D, G, src, trg, curriculum=None):
        src_len = min(curriculum, len(src)-1) + 1
        trg_len = min(curriculum, len(src)-1) + 1
        gen_trg, context = G(src[:src_len], trg[:trg_len])
        loss_g = D(gen_trg, context)
        loss = -loss_g.mean()
        return loss

    def criterion_d(self, D, G, src, trg, lambd, curriculum=None):
        src_len = min(curriculum, len(src)-1) + 1
        trg_len = min(curriculum, len(src)-1) + 1
        # with gen
        gen_trg, context = G(src[:src_len], trg[:trg_len])
        d_gen = D(gen_trg, context)
        # with real
        trg = to_onehot(trg, D.vocab_size).type(torch.FloatTensor)[1:trg_len]
        trg = Variable(trg.cuda())
        d_real = D(trg, context)
        # calculate gradient panalty
        penalty = grad_penalty(D, trg.data, gen_trg.data, context.data, lamb)
        loss = d_gen.mean() - d_real.mean() + penalty
        return loss

    def trainer(self, optimizer, target=None, cuda=False):

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
        return adv_x
