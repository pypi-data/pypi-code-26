from __future__ import absolute_import, division, print_function

from toxic.attack import Attack


# TODO
class LBFGS(Attack):
    """ Formalizes the generation of adversarial examples as an optimization
    problem.
    Reference:
        Exploring the Space of Adversarial Images,
        Tabacof et al., https://arxiv.org/abs/1510.05328
    """
    def __init__(self, model, lr=0.01, reg=0.01, momentum=0.9, max_iter=10):
        super(LBFGS, self).__init__()
        if not isinstance(model, nn.Module):
            raise ValueError('model must be an instance of nn.Module')
        self.model = model
        self.lr = lr
        self.reg = reg
        self.momentum = momentum
        self.max_iter = max_iter

    def criterion(self, x, probs, original_x, targets):
        model_loss = F.cross_entropy(probs, targets)
        image_loss = F.mse_loss(x, original_x)
        loss = model_loss + self.reg * image_loss
        return loss

    def generate(self, x, y=None, target=None):

        def iter_x(self, x): # TODO replace this with adv_x
            yield x

        adv_x = Varialbe(x.data, requires_grad=True)
        optimizer = SGD(iter_x(x), lr=self.lr, momentum=self.momentum)

        # TODO: clamp images
        probs = self.model(x)
        if apply_softmax:
            probs = F.softmax(probs, dim=1)
        preds = torch.max(probs.data, 1)[1]
        original_preds = preds.clone()

        # TODO: non-target
        targets = Variable(torch.LongTensor([target] * self.batch_size))

        i = 0
        while i < self.max_iter and torch.all(original_preds != preds):
            optimizer.zero_grad()

            # TODO: clamp loss so that all pixels are in range [0, 1]
            probs = self.model(adv_x)
            if self.apply_softmax:
                probs = F.softmax(probs, dim=1)
            loss = F.cross_entropy(adv_x, probs, x, targets)
            pred_loss, preds = torch.max(probs.data, 1)

            loss = self.criterion(adv_x, probs, x, targets)
            loss.backward()
            optimizer.step()

        return adv_x
