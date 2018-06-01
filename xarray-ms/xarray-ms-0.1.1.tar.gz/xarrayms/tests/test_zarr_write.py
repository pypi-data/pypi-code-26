from __future__ import print_function

import argparse
import logging
import os
import os.path

import dask.array as da
from dask.diagnostics import ProgressBar, Profiler
from xarrayms import xds_from_ms
import zarr

logging.basicConfig(format="%(levelname)s - %(message)s", level=logging.WARN)


def create_parser():
    p = argparse.ArgumentParser()
    p.add_argument("ms")

    return p


args = create_parser().parse_args()

store = zarr.DirectoryStore("zarr_data")
group = zarr.hierarchy.group(store=store, overwrite=True,
                             synchronizer=zarr.ThreadSynchronizer())

with ProgressBar(), Profiler() as prof:
    for i, ds in enumerate(xds_from_ms(args.ms)):

        _, ms = os.path.split(args.ms.rstrip(os.sep))

        field_id = ds.attrs['FIELD_ID']
        data_desc_id = ds.attrs['DATA_DESC_ID']

        group_str = '%s/FIELD_ID_%s/DATA_DESC_ID_%s' % (ms,
                                                        field_id,
                                                        data_desc_id)

        ds_group = group.create_group(group_str)
        compressor = zarr.Blosc(cname='zstd', clevel=3, shuffle=2)
        ds.to_zarr(store, 'w', zarr.ThreadSynchronizer(), group_str)

    prof.visualize(file_path="prof.html")
