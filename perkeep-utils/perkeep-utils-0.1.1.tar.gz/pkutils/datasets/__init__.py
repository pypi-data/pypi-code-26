#
# -*- coding: utf-8 -*-
# python-perkeep-utils
# Copyright (C) 2018  Markus Peröbner
#
'''Tools for reading, writing and manipulating datasets.

Writing a dataset:
    with pkutils.datasets.FileSystemDatasetWriter('some/ds', [
        {
            "id": "tread_left_velocity",
            "type": "float",
        },
    ]) as ds:
        for e in some_input:
            ds.append([
                e.value,
            ])

Appending a random value to a written dataset:
    ds = pkutils.datasets.RandomSampleDatasetWriter(ds)

Reading a dataset and splitting:
    ds = pkutils.datasets.build_from_resource_identifier('pk:attr:"per:type":dataset')
    sample_categories = pkutils.datasets.split(ds.samples)
'''
from .common import UnionDatasetReader, ShuffleDatasetReader, split, RandomSampleDatasetWriter, MappingSample, MixinSample
from .fs import FileSystemDatasetReader, FileSystemDatasetWriter
from .pipeline import Pipeline
from .pk import PerkeepDatasetReader, PerkeepDatasetWriter
from .uri import build_from_resource_identifier
