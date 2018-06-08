from __future__ import absolute_import, division, print_function

import torch


# Evaluation Functions

def topk_miss(probs, target, k):
    r"""Computes number of misses that are not included in top k predictions."""
    return probs.size(-1) - topk_correct(probs, target, k)


def topk_correct(probs, target, k):
    r"""Computes number of correct answers in top k."""
    _, pred = torch.topk(probs, k)
    pred = pred.t()
    correct = pred.eq(target.view(1, -1).expand_as(pred))
    correct_k = correct.view(-1).sum(0, keepdim=True)
    return correct_k.cpu()[0]

def topk_accuracy(probs, target, k):
    r"""Computes accuracy of the batch."""
    batch_size = target.size(0)
    correct_k = topk_correct(probs, target, k)
    return correct_k * (100.0 / batch_size)


class Metric(object):
    def __init__(self):
        pass

    def update(self):
        pass

    def reset(self):
        pass

    def accuracy(self):
        pass
