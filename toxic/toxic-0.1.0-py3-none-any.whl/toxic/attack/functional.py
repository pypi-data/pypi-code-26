from __future__ import absolute_import, division, print_function

import torch
import numpy as np
from torch.autograd import grad, Variable
from torch.nn import functional as F
from toxic.util import l2_batch_norm, kl_div
from torch.autograd.gradcheck import zero_gradients


def jacobian(x, target):
    """ Compute the Jacobian value corresponding to each pair of x and target.
    It helps us to estimate how changes in x affect each of the class
    probability.
    """
    if not x.requires_grad:
        raise ValueError('x must set require_grad to True')

    n_classes = target.size(1)
    jacobian_val = torch.zeros(n_classes, *x.size())
    grads = torch.zeros(*target.size())
    if x.is_cuda:
        jacobian_val = jacobian_val.cuda()
        grads = grads.cuda()

    # Compute gradients for all classes
    for i in range(n_classes):
        zero_gradients(x)
        grads.zero_()
        grads[:, i] = 1
        target.backward(grads, retain_variables=True)
        jacobian_val[i] = x.grad.data
    return jacobian_val.transpose(0, 1)


def saliency_map(jacobian, search_domain, target_index, increase=True):
    """ Computes Saliency Map, which determines the best pixels for our
    adversarial goal. It takes account of not just target class, but all other
    classes.
    Args:
        jacobian:
    """
    alpha = jacobian[target_index].squeeze()
    beta = torch.sum(jacobian, 0).squeeze() - alpha

    # Create a mask to keep features that match saliency map conditions
    if increase:
        m1, m2 = torch.ge(alpha, 0.0), torch.le(beta, 0.0)
    else:
        m1, m2 = torch.le(alpha, 0.0), torch.ge(beta, 0.0)
    mask = torch.mul(torch.mul(m1, m2), search_domain)

    if increase:
        scores = torch.mul(torch.mul(alpha, torch.abs(beta)), mask)
    else:
        scores = torch.mul(torch.mul(torch.abs(alpha), beta), mask)

    max_val, max_idx = torch.max(scores, dim=0)
    return max_val, max_idx


def fgsm(x, pred, eps=0.3, clip_min=None, clip_max=None):
    r""" Generates adversarial examples based on Fast Gradient Sign Method (FGSM)
    Args:
        x (Variable): Input variable.
        pred (Variable): Prediction of the model. (output of the softmax)
        y (Variable): (optional) One hot encoded target label.
        eps (float): Attack step size.
        ord (int): (optional) Order of the norm (np.inf, 1 or 2).
        clip_min (float): Minimum component value.
        clip_max (float): Maximum component value.
        targeted (bool): true or false
    Returns:
        adv_x (Variable):
            Generated adversarial example.
    Reference:
        Explaining and Harnessing Adversarial Examples,
        Goodfellow et al., CoRR2014, https://arxiv.org/abs/1412.6572
    """
    return fgm(x, pred, y=None, eps=eps, ord=np.inf,
               clip_min=clip_min, clip_max=clip_max)


def fgm(x, pred, y=None, eps=0.3, ord=np.inf,
        clip_min=None, clip_max=None, targeted=False):
    r""" Generates adversarial examples based on Fast Gradient Method (FGM)
    Args:
        x (Variable): Input variable.
        pred (Variable): Prediction of the model. (output of the softmax)
        y (Variable): (optional) One hot encoded target label.
        eps (float): Attack step size.
        ord (int): (optional) Order of the norm (np.inf, 1 or 2).
        clip_min (float): Minimum component value.
        clip_max (float): Maximum component value.
        targeted (bool): true or false
    Returns:
        adv_x (Variable):
            Generated adversarial example.
    Reference:
        Explaining and Harnessing Adversarial Examples,
        Goodfellow et al., CoRR2014, https://arxiv.org/abs/1412.6572
    """
    if y is None:
        # use model prediction as the label
        _, y = torch.max(pred, 1)
    # compute loss
    loss = F.cross_entropy(pred, y, size_average=False)
    if targeted:
        loss = -loss
    # get gradients wrt x
    gradient = grad(loss, x)[0]

    if ord == np.inf:
        # L-inf (sign)
        norm_grad = torch.sign(gradient)
    else:
        # Lp normalization
        norm_grad = F.normalize(gradient, ord)
    # add perturbation
    scaled_grad = eps * norm_grad
    adv_x = x + scaled_grad
    # clip by the range [clip_min, clip_max]
    if (clip_min is not None) and (clip_max is not None):
        adv_x = torch.clamp(adv_x, clip_min, clip_max)
    return adv_x


def lds(model, x, pred, eps=8., iterations=1, xi=1e-6,
        apply_softmax=True, batch_norm=True):
    r""" Computes local distributional smoothness (LDS) for Virtual Adversarial
    Training (VAT) with extension of l2 batch norm
    Args:
        model (nn.Module): The model that returns unnormalized logits.
        x (Variable): Input variable. (output of the softmax)
        logits (Variable): Output of the model (input to the softmax layer)
        eps (float): Attack step size.
        xi (float): the finite difference parameter
    Returns:
        adv_x (Variable):
            Generated adversarial example.
        lds (Variable):
            The LDS value.
    Reference:
        Distributional Smoothing With Virtual Adversarial Training
        https://arxiv.org/abs/1507.00677
    """
    y1 = Variable(pred.data)
    adv_x = vatm(model, x, pred, eps, iterations, xi,
                 apply_softmax, batch_norm)
    y2 = model(adv_x)
    if apply_softmax:
        y2 = F.softmax(y2, dim=1)
    return -kl_div(y1, y2)


def vatm(model, x, pred, eps=8., iterations=1, xi=1e-6,
         apply_softmax=True, batch_norm=True):
    r""" Generates adversarial sample based on Virtual Adversarial Training (VAT)
    Method with extension of l2 batch norm
    Args:
        model (nn.Module): The model that returns unnormalized logits.
        x (Variable): Input variable. (output of the softmax)
        logits (Variable): Output of the model (input to the softmax layer)
        eps (float): Attack step size.
        xi (float): the finite difference parameter
    Returns:
        adv_x (Variable):
            Generated adversarial example.
        lds (Variable):
            The LDS value.
    Reference:
        Distributional Smoothing With Virtual Adversarial Training
        https://arxiv.org/abs/1507.00677
    """
    y1 = Variable(pred.data)
    d = Variable(torch.randn(x.size()))
    for i in range(iterations):
        y2 = model(x + xi * d)
        if apply_softmax:
            y2 = F.softmax(y2, dim=1)
        kl = kl_div(y1, y2)
        gradient = grad(kl, x)[0]
        d = Variable(gradient.data)
        if batch_norm:
            d = l2_batch_norm(d)
    adv_x = x + eps * d
    return adv_x
