#
# -*- coding: utf-8 -*-
# python-perkeep-utils
# Copyright (C) 2018  Markus Peröbner
#
from . import common
import json
import os
from PIL import Image
import random

class FileSystemDatasetReader(object):
    '''Loads a dataset from the file system.

    A file system dataset is made of the follwing components:
    - a root directory
    - a dataset.json file within the root directory
    - additional data fragments (like images) within the root directory

    The dataset.json might look like this:
    {
        "probes": [
            {
                "id": "tread_left_velocity",
                "type": "float"
            },
            {
                "id": "camera",
                "type": "image"
            },
            {
                "id": "random",
                "type": "float"
            }
        ],
        "samples": [
            [0.1234567, "img0.jpg", 0.3534564788]
        ],
        "globals": [
            {
                "id": "track_visible",
                "type": "boolean",
                "value": true
            }
        ]
    }
    '''

    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.__dataset = None

    @property
    def _dataset(self):
        if(self.__dataset is None):
            json_path = os.path.join(self.dataset_path, 'dataset.json')
            with open(json_path, 'r') as f:
                self.__dataset = json.load(f)
        return self.__dataset

    @property
    def _probes(self):
        return self._dataset['probes']

    @property
    def _globals(self):
        return self._dataset['globals'] if 'globals' in self._dataset else []

    @property
    def probes(self):
        return self._probes + self._globals

    @property
    def sample_count(self):
        return len(self._dataset['samples'])
    
    @property
    def samples(self):
        dataset = self._dataset
        probe_by_id = dict([(p['id'], common.Probe(i, p['type'])) for i, p in enumerate(self._probes)])
        global_by_id = dict([(p['id'], common.Probe(i, p['type'], p['value'])) for i, p in enumerate(self._globals)])
        for sample in dataset['samples']:
            yield FileSystemSample(self.dataset_path, self._globals, self._probes, global_by_id, probe_by_id, sample)

class FileSystemSample(common.Sample):
    
    IDENTITY_TYPES = set([
        'boolean',
        'float',
        'string',
    ])

    def __init__(self, dataset_path, globals, probes, global_by_id, probe_by_id, sample):
        self.dataset_path = dataset_path
        self._globals = globals
        self._probes = probes
        self._global_by_id = global_by_id
        self._probe_by_id = probe_by_id
        self.sample = sample

    def __getitem__(self, probe_id):
        probe = None
        probe_value = None
        if(probe_id in self._probe_by_id):
            probe = self._probe_by_id[probe_id]
            probe_value = self.sample[probe.index]
        if(probe_id in self._global_by_id):
            probe = self._global_by_id[probe_id]
            probe_value = probe.default_value
        if(probe is None):
            return None
        if(probe.type in FileSystemSample.IDENTITY_TYPES):
            return probe_value
        if(probe.type == 'image'):
            image_path = os.path.join(self.dataset_path, probe_value)
            return Image.open(image_path)
        raise Error('Unknown probe type: {}'.format(probe.type))

    def keys(self):
        return self._probe_by_id.keys() + self._global_by_id.keys()

    @property
    def values(self):
        return [self[probe['id']] for probe in self._probes] + [self[probe['id']] for probe in self._globals]

class FileSystemDatasetWriter(object):
    '''Writes a dataset to the file system.

    Example usage:
    probes = [
        {
            "id": "random",
            "type": "float",
        },
    ]
    with FileSystemDatasetWriter('path/to/recording_dir', probes) as w:
        w.append([0.1234567])
    '''

    def __init__(self, dataset_path, probes, image_format='jpg'):
        self.dataset_path = dataset_path
        self.probes = probes
        self.image_format = image_format
        self.samples = []
        self._next_image_id = 0

    def __enter__(self):
        os.mkdir(self.dataset_path)
        return self

    def __exit__(self, *args, **kwargs):
        self._write_dataset()

    def _write_dataset(self):
        json_path = os.path.join(self.dataset_path, 'dataset.json')
        with open(json_path, 'w') as f:
            dataset = {
                "probes": self.probes,
                "samples": self.samples,
            }
            json.dump(dataset, f)

    def append(self, probe_values):
        sample = [self._map_probe_value(self.probes[i], v) for i, v in enumerate(probe_values)]
        self.samples.append(sample)

    def _map_probe_value(self, probe, probe_value):
        probe_type = probe['type']
        if(probe_type == 'float'):
            return probe_value
        if(probe_type == 'image'):
            image_file_name = 'img_{}_{}.{}'.format(self._next_image_id, probe['id'], self.image_format)
            self._next_image_id += 1
            probe_value.save(os.path.join(self.dataset_path, image_file_name))
            return image_file_name
        if(probe_type == 'string'):
            return probe_value
        raise Error('Unknown probe type: {}'.format(probe_type))
