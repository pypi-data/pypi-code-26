#
# -*- coding: utf-8 -*-
# python-perkeep-utils
# Copyright (C) 2018  Markus Peröbner
#
from . import common
import io
import json
import pkutils
from PIL import Image

class PerkeepDatasetExpressionReader(common.LazyDatasetReader):
    def __init__(self, expression):
        super(PerkeepDatasetExpressionReader, self).__init__()
        self.expression = expression

    def build_dataset(self):
        results = pkutils.query({
            'expression': self.expression,
            'describe': {
                'depth': 1,
            },
        })

        def build_dataset_for_blob(blob):
            description = results['description']['meta'][blob['blob']]
            content_ref = description['permanode']['attr']['camliContent'][0]
            return PerkeepDatasetReader(content_ref)

        datasets = [build_dataset_for_blob(blob) for blob in results['blobs']]
        return common.UnionDatasetReader(datasets)

class PerkeepDatasetReader(object):
    def __init__(self, dataset_content_ref):
        self.dataset_content_ref = dataset_content_ref
        self.__dataset = None

    @property
    def _dataset(self):
        if(self.__dataset is None):
            with pkutils.download(self.dataset_content_ref) as req:
                self.__dataset = json.load(req)
        return self.__dataset

    @property
    def probes(self):
        return self._dataset['probes']

    @property
    def sample_count(self):
        return len(self._dataset['samples'])
    
    @property
    def samples(self):
        dataset = self._dataset
        probe_by_id = dict([(p['id'], common.Probe(i, p['type'])) for i, p in enumerate(dataset['probes'])])
        for sample in dataset['samples']:
            yield PerkeepSample(probe_by_id, sample)

class PerkeepSample(common.Sample):

    IDENTITY_TYPES = set([
        'boolean',
        'float',
        'string',
    ])
    
    def __init__(self, probe_by_id, sample):
        self.probe_by_id = probe_by_id
        self.sample = sample

    def __getitem__(self, probe_id):
        if(not probe_id in self.probe_by_id):
            return None
        probe = self.probe_by_id[probe_id]
        probe_value = self.sample[probe.index]
        if(probe.type in PerkeepSample.IDENTITY_TYPES):
            return probe_value
        if(probe.type == 'image'):
            with pkutils.download(probe_value) as req:
                return Image.open(req)
        if(probe.type == 'audio'):
            with pkutils.download(probe_value) as req:
                # data = io.BytesIO(req.read())
                # return soundfile.read(data)
                raise Exception('audio support not yet implemented')
        raise Exception('Unknown probe type: {}'.format(probe.type))

    def keys(self):
        return self.probe_by_id.keys()

class PerkeepDatasetWriter(object):
    def __init__(self, probes, image_format='jpeg', permanode_attributes={}):
        self.probes = probes
        self.image_format = image_format
        self.permanode_attributes = permanode_attributes
        self.samples = []
        
    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self._write_dataset()

    def _write_dataset(self):
        dataset = {
            "probes": self.probes,
            "samples": self.samples,
        }
        content_ref = pkutils.upload(json.dumps(dataset).encode('utf-8'), 'dataset.json')
        permanode_attributes = self.permanode_attributes.copy()
        permanode_attributes['camliContent'] = content_ref
        pkutils.persist(permanode_attributes)

    def append(self, probe_values):
        sample = [self._map_probe_value(self.probes[i], v) for i, v in enumerate(probe_values)]
        self.samples.append(sample)

    def _map_probe_value(self, probe, probe_value):
        probe_type = probe['type']
        if(probe_type == 'float'):
            return probe_value
        if(probe_type == 'image'):
            image_buffer = io.BytesIO()
            probe_value.save(image_buffer, self.image_format)
            file_name = '{}.{}'.format(probe['id'], self.image_format)
            return pkutils.upload(image_buffer.getvalue(), file_name)
        if(probe_type == 'string'):
            return probe_value
        raise Exception('Unknown probe type: {}'.format(probe_type))
