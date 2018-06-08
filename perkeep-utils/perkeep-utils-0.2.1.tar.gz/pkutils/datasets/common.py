#
# -*- coding: utf-8 -*-
# python-perkeep-utils
# Copyright (C) 2018  Markus Peröbner
#
import random

class Probe(object):
    def __init__(self, index, type, default_value=None):
        self.index = index
        self.type = type
        self.default_value = default_value

class Sample(object):
    def __repr__(self):
        d = dict([(k, self[k]) for k in self.keys()])
        return '{}'.format(d)

class DelegateSample(Sample):
    def __init__(self, delegate):
        super(DelegateSample, self).__init__()
        self.delegate = delegate

    def __getitem__(self, probe_id):
        return self.delegate[probe_id]
    
    def keys(self):
        return self.delegate.keys()

class MappingSample(DelegateSample):
    def __init__(self, delegate, mapper):
        super(MappingSample, self).__init__(delegate)
        self.mapper = mapper

    def __getitem__(self, probe_id):
        return self.mapper(probe_id, self.delegate)

class MixinSample(DelegateSample):
    def __init__(self, delegate, extra_properties, overwrite=True):
        super(MixinSample, self).__init__(delegate)
        self.extra_properties = extra_properties
        self.overwrite = overwrite

    def __getitem__(self, probe_id):
        dict0 = self.extra_properties if self.overwrite else self.delegate
        if(probe_id in dict0):
            return dict0[probe_id]
        dict1 = self.delegate if self.overwrite else self.extra_properties
        return dict1[probe_id]

    def keys(self):
        return list(set(list(self.delegate.keys()) + list(self.extra_properties.keys())))

class UnionDatasetReader(object):
    def __init__(self, datasets):
        self.datasets = datasets

    @property
    def probes(self):
        if(len(self.datasets) == 0):
            return {}
        probes = self.datasets[0].probes
        for ds in self.datasets[1:]:
            if(probes != ds.probes):
                # TODO right now returned sample value arrays are not
                # adjusted. that's why a difference in probes is not
                # possible right now.
                raise Exception('Probes in UnionDatasetReader missmatch. {} VS. {}'.format(probes, ds.probes))
        return probes

    @property
    def sample_count(self):
        count = 0
        for ds in self.datasets:
            count += ds.sample_count
        return count

    @property
    def samples(self):
        for ds in self.datasets:
            for sample in ds.samples:
                yield sample

class ShuffleDatasetReader(object):
    def __init__(self, dataset):
        self.dataset = dataset

    @property
    def probes(self):
        return self.dataset.probes

    @property
    def sample_count(self):
        return self.dataset.sample_count

    @property
    def samples(self):
        samples = [s for s in self.dataset.samples]
        random.shuffle(samples)
        return samples

class LazyDatasetReader(object):
    '''Instantiates a dataset on the first access.

    Extending classes must implement a build_dataset(self) method.
    '''

    def __init__(self):
        self._dataset = None

    @property
    def probes(self):
        if(self._dataset is None):
            self._dataset = self.build_dataset()
        return self._dataset.probes

    @property
    def dataset(self):
        if(self._dataset is None):
            self._dataset = self.build_dataset()
        return self._dataset

    @property
    def sample_count(self):
        return self.dataset.sample_count

    @property
    def samples(self):
        return self.dataset.samples

DEFAULT_CATEGORIES = {
    'train': 0.8,
    'validate': 0.1,
    'test': 0.1,
}

def split(samples, categories=DEFAULT_CATEGORIES, random_id='random'):
    max_r_array = [e for e in build_max_random_values(categories)]

    def get_category(r):
        if(r is None):
            r = random.random()
        for name, max_r in max_r_array:
            if(r <= max_r):
                return name
        raise Exception('We should not have been here :( r={}'.format(r))

    samples_by_category = dict([(name, []) for name, weight in categories.items()])
    for sample in samples:
        category = get_category(sample[random_id])
        samples_by_category[category].append(sample)
    return samples_by_category

def build_max_random_values(categories):
    weight_sum = calc_weight_sum(categories)
    current_sum = 0
    for name, weight in categories.items():
        current_sum += weight
        yield (name, current_sum / weight_sum)

def calc_weight_sum(categories):
    ws = 0
    for name, weight in categories.items():
        ws += weight
    return ws

class DelegateDatasetWriter(object):
    def __init__(self, delegate_dataset):
        self.delegate = delegate_dataset
    
    @property
    def probes(self):
        return self.delegate.probes

    def __enter__(self):
        self.delegate.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        self.delegate.__exit__(*args, **kwargs)

    def append(self, *args, **kwargs):
        self.delegate.append(*args, **kwargs)

class RandomSampleDatasetWriter(DelegateDatasetWriter):
    def __init__(self, delegate_dataset, probe_id="random"):
        delegate_dataset.probes.append({
            "id": probe_id,
            "type": "float"
        })
        super(RandomSampleDatasetWriter, self).__init__(delegate_dataset)

    def append(self, samples):
        samples.append(random.random())
        super(RandomSampleDatasetWriter, self).append(samples)
