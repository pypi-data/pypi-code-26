#
# -*- coding: utf-8 -*-
# python-perkeep-utils
# Copyright (C) 2018  Markus Peröbner
#
'''Defines a pipeline for preparing samples for a training.

Samples will be passed through the following stepes within a pipeline:
S1) filter samples
S2) reduce to needed probes
S3) split into train/validate/test samples
S4) extend train samples set by generated ones
S5) shuffle samples
S6) map to xy arrays
S7) group xy arrays into batches

pl = pkutils.datasets.Pipeline()
pl.filters.append(lambda s: s['value'] > 0.5)
pl.reducers.append(['value'])
pl.categories = {
    'train': 0.8,
    'validation': 0.1,
    'test': 0.1,
}
pl.extenders.append(a_generator)
pl.x_mapper = lambda s: s['in']
pl.y_mapper = lambda s: s['out']
pl.batch_size = 128
pl.shuffle = True

# performes S1 and S2
pl.append_reduced_samples(input_samples, output_samples)

samples = pl.get(input_samples)
len(samples)
it = iter(samples)
it = samples.batch_arrays()

samples_by_category = pl.split(input_samples)
len(samples_by_category['train'])
it = iter(samples_by_category['train'])
it = samples_by_category['train'].batch_arrays()
'''

from . import common
import itertools
import numpy as np
import random

class Pipeline(object):
    def __init__(self):
        self.filters = []
        self.reducers = []
        self.categories = {
            'train': 0.8,
            'validation': 0.1,
            'test': 0.1,
        }
        self.extenders = []
        self.x_mapper = identity
        self.y_mapper = identity
        self.batch_size = 128
        self.shuffle = True

    def append_reduced_samples(self, samples_input, samples_output):
        # TODO the api is right now unable to predict the probes settings
        for sample in self._reduced_samples(samples_input):
            samples_output.append(sample)

    def get(self, samples):
        samples = self._reduced_samples(samples)
        samples = self._extended_samples(samples)
        samples = list(samples)
        if(self.shuffle):
            random.shuffle(samples)
        return XYAdapter(samples, self._mapper, self.batch_size)

    def split(self, samples):
        reduced_samples = list(self._reduced_samples(samples))
        splitted_samples = common.split(reduced_samples, self.categories)
        if('train' in splitted_samples):
            splitted_samples['train'] = list(self._extended_samples(splitted_samples['train']))
            if(self.shuffle):
                random.shuffle(splitted_samples['train'])
        return dict([(c, XYAdapter(s, self._mapper, self.batch_size)) for c, s in splitted_samples.items()])

    def _mapper(self, sample):
        x = self.x_mapper(sample)
        y = self.y_mapper(sample)
        return (x, y)

    def _reduced_samples(self, samples):
        for sample in samples:
            if(len(self.filters) > 0 and not any(map(lambda f: f(sample), self.filters))):
                continue
            sample = self._reduce_sample(sample)
            yield sample

    def _reduce_sample(self, sample):
        for reducer in self.reducers:
            if(callable(reducer)):
                sample = reducer(sample)
            else:
                sample = ReducedSample(sample, reducer)
        return sample

    def _extended_samples(self, samples):
        for sample in samples:
            extended_samples = [sample]
            for extender in self.extenders:
                extended_samples = itertools.chain(*[extender(s) for s in extended_samples])
            for se in extended_samples:
                yield se

class Stop(object):
    pass

STOP = Stop()

class ReducedSample(common.DelegateSample):
    def __init__(self, delegate, reduction):
        super(ReducedSample, self).__init__(delegate)
        self.reduction = reduction
        self.reduction_set = frozenset(reduction)

    def __getitem__(self, probe_id):
        if(probe_id in self.reduction_set):
            return self.delegate[probe_id]
        else:
            return None

    def keys(self):
        return self.reduction

class XYAdapter(object):
    def __init__(self, samples, mapper, batch_size):
        self.samples = samples
        self.mapper = mapper
        self.batch_size = batch_size

    def __len__(self):
        return len(self.samples)

    def __iter__(self):
        for sample in self.samples:
            yield self.mapper(sample)

    def infinite(self):
        while True:
            for sample in self:
                yield sample

    def batch_arrays(self):
        sample_iter = iter(self.infinite())
        while True:
            x_array = []
            y_array = []
            for i in range(self.batch_size):
                x, y = next(sample_iter)
                x_array.append(x)
                y_array.append(y)
            yield np.array(x_array), np.array(y_array)

def identity(x):
    return x
