import os
from tensorboardX import SummaryWriter


class Grapher:

    def __init__(self, dout):
        self.writer = SummaryWriter(os.path.join(dout, 'tensorboard'))
        self.plotted_module = False

    def plot_module(self, module, args):
        if not isinstance(args, (list, tuple)):
            args = (args, )
        self.writer.add_graph(module, args)
        self.plotted_module = True

    def add_metrics(self, metrics, iteration):
        keys = sorted(list(set(list(metrics['train'].keys()) + list(metrics['dev'].keys()))))
        for k in keys:
            v = {}
            if k in metrics['train']:
                v['train'] = metrics['train'][k]
            if k in metrics['dev']:
                v['dev'] = metrics['dev'][k]
            if v:
                self.writer.add_scalars(k, v, iteration)

    def add_embeddings(self, embeddings, labels, iteration):
        self.writer.add_embedding(embeddings, metadata=labels, iteration=iteration)

    def add_parameters(self, module, iteration):
        for name, p in module.named_parameters():
            self.writer.add_histogram(name, p.detach().numpy(), iteration)
