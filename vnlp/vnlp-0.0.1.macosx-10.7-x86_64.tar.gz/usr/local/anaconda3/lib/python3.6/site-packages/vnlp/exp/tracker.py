import os
import logging
import json
import re
import torch
from argparse import Namespace


class Tracker:

    def __init__(self, log=None, epoch=0, iteration=0):
        self.log = log or []
        self.epoch = epoch
        self.iteration = iteration
        self.writer = None

    def save(self, fname):
        with open(fname, 'wt') as f:
            json.dump({'log': self.log, 'epoch': self.epoch, 'iteration': self.iteration}, f, indent=2)

    @classmethod
    def load(cls, fname):
        with open(fname) as f:
            return cls(**json.load(f))

    def best(self, early_stop, reverse=True):
        sort = sorted(self.log, key=lambda m: m['dev'][early_stop], reverse=reverse)
        return sort[0]

    def is_best(self, metrics, early_stop, iteration, epoch, reverse=True):
        self.iteration = iteration
        self.epoch = epoch
        better = True
        if self.log:
            best = self.best(early_stop, reverse=reverse)
            better = metrics['dev'][early_stop] >= best['dev'][early_stop] if reverse else metrics['dev'][early_stop] <= best['dev'][early_stop]
        self.log.append(metrics.copy())
        return better

    @classmethod
    def save_data(cls, data, fname, verbose=True):
        logging.info('Saving file {}'.format(fname))
        with open(fname, 'wt') as f:
            json.dump(data, f)

    @classmethod
    def find_checkpoints(cls, root, early_stop):
        files = [f for f in os.listdir(root) if f.endswith('.pt')]
        score_re = re.compile(r'{}=([0-9.\-]+)'.format(early_stop))
        files = []
        for f in os.listdir(root):
            scores = score_re.findall(f)
            if f.endswith('.pt') and scores:
                files.append((os.path.join(root, f), float(scores[0].rstrip('.'))))
        files.sort(key=lambda tup: tup[-1], reverse=True)
        return files

    @classmethod
    def clean_old_checkpoints(cls, root, early_stop, keep=5):
        files = cls.find_checkpoints(root, early_stop)
        if len(files) > keep:
            for f, s in files[keep:]:
                os.remove(f)

    def save_checkpoint(self, dout, metrics, early_stop, module, optimizer, args, link_best=False):
        fcheckpoint = os.path.join(dout, 'checkpoint.epoch={},iter={},{}={}.pt'.format(self.epoch, self.iteration, early_stop, metrics['dev'][early_stop]))
        torch.save({
            'metrics': metrics,
            'module': module.state_dict(),
            'optimizer': optimizer.state_dict(),
            'epoch': self.epoch,
            'iteration': self.iteration,
            'args': args,
        }, fcheckpoint)
        if link_best:
            fbest = os.path.join(dout, 'checkpoint.best.pt')
            if os.path.islink(fbest):
                os.unlink(fbest)
            os.symlink(fcheckpoint, fbest)

    @classmethod
    def load_best_checkpoint(cls, root, early_stop):
        files = cls.find_checkpoints(root, early_stop)
        if not files:
            raise Exception('No checkpoints found in {} with early stopping metric {}'.format(root, early_stop))
        fbest = files[0][0]
        logging.info('Loading {}'.format(fbest))
        return torch.load(fbest)
