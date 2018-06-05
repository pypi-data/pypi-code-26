"""
Helper functions for reading and writing objects to files
"""

import h5py
import pickle
import tempfile


def add_items_to_tarfile_hdf5(tar_file, items, arcname):
    """ Add items to one hdf5 file """
    temp_file = tempfile.NamedTemporaryFile()
    hf = h5py.File(temp_file.name)
    for key, value in items.items():
        hf.create_dataset(key, data=value)
    hf.close()
    temp_file.seek(0)
    tar_info = tar_file.gettarinfo(arcname=arcname, fileobj=temp_file)
    tar_file.addfile(tar_info, temp_file)
    temp_file.close()


def add_items_to_tarfile_pickle(tar_file, items, arcname):
    """ Add items by pickling them """
    temp_file = tempfile.TemporaryFile()
    pickle.dump(items, temp_file)
    temp_file.seek(0)
    tar_info = tar_file.gettarinfo(arcname=arcname, fileobj=temp_file)
    tar_file.addfile(tar_info, temp_file)
    temp_file.close()


def add_items_to_tarfile_custom(tar_file, items):
    """ Add items assuming they have a custom write function """
    for key, value in items.items():
        temp_file = tempfile.TemporaryFile()
        value.write(temp_file)
        temp_file.seek(0)
        tar_info = tar_file.gettarinfo(arcname=key, fileobj=temp_file)
        tar_file.addfile(tar_info, temp_file)
        temp_file.close()


def add_list_to_tarfile_custom(tar_file, objects, arcname):
    """ Add list of objects assuming they have a custom write function """
    for i, obj in enumerate(objects):
        temp_file = tempfile.TemporaryFile()
        obj.write(temp_file)
        temp_file.seek(0)
        fname = '{}_{}'.format(arcname, i)
        tar_info = tar_file.gettarinfo(arcname=fname, fileobj=temp_file)
        tar_file.addfile(tar_info, temp_file)
        temp_file.close()


def read_items_hdf5(tar_file, arcname):
    """ Read items from hdf5file inside tar_file """

    # read hdf5
    temp_file = tempfile.NamedTemporaryFile()
    temp_file.write(tar_file.extractfile(arcname).read())
    temp_file.seek(0)
    hf = h5py.File(temp_file.name, 'r')
    items = {key: value[:] for key, value in hf.items()}
    hf.close()
    return items


def read_items_pickle(tar_file, arcname):
    items = dict()
    items = pickle.load(tar_file.extractfile(arcname))
    return items


def read_list_custom(tar_file, arcname, read_function, **kwargs):
    objects = []
    i = 0
    while True:
        try:
            fname = '{}_{}'.format(arcname, i)
            f = tar_file.extractfile(fname)
            obj = read_function(f, **kwargs)
            objects.append(obj)
            f.close()
        except KeyError:
            break
        i += 1
    return objects
