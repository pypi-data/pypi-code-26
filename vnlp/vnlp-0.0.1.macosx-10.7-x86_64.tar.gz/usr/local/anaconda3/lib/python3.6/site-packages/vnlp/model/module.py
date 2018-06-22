from torch import nn


class BaseModule(nn.Module):

    def __init__(self, args):
        super().__init__()
        self.args = args

    def featurize(self, batch, device=None):
        raise NotImplementedError()

    def compute_loss(self, out, batch):
        raise NotImplementedError()

    def extract_preds(self, out, batch):
        raise NotImplementedError()

    def graph(self, grapher, metrics, iteration):
        grapher.add_metrics(metrics, iteration=iteration)
        grapher.add_parameters(self, iteration)
