"""Utility functions."""
import numpy as np


def caffe_load_image(image_filename):
    """Load image using caffe.io.load_image.

    This is to maintain shape expectation across the caffe library.

    Args:
        image_filename (str): String filename.

    Returns:
        numpy.ndarray: an image with the following properties:
            shape: [Height, Width, Channels]
            channel_order: RGB
            scale: [0, 1]
            dtype: np.float32
    """
    import caffe
    return caffe.io.load_image(image_filename, color=True)


def caffe_load_image_batch(image_filenames, batch_size=None):
    """Load image using caffe.io.load_image.

    This is to maintain shape expectation across the caffe library.

    Args:
        image_filename (list of str): List of string filenames.
        batch_size (int): If batch_size is None, then all filenames are read.
            Otherwise only the first `batch_size` number of filenames are read.

    Returns:
        numpy.ndarray: an image with the following properties:
            shape: [batch_size, Height, Width, Channels]
            channel_order: RGB
            scale: [0, 1]
            dtype: np.float32
    """
    if batch_size is None:
        batch_size = len(image_filenames)

    image_batch = [caffe_load_image(image_filename) for image_filename in image_filenames[:batch_size]]
    image_batch = np.array(image_batch)  # converting list into numpy array

    return image_batch


# TODO (nitred): LRU cache
def get_caffe_transformer(net_input_shape, mean_bgr_255=None):
    """Transform a batch of images which were loaded by caffe.io.load_image.

    Transformations:
        - mean subtraction (if mean provided)
        - transposes data to become [Channels x Height x Width]
        - swaps channels to convert RGB to BGR
        - scales the data to [0., 255.]

    Args:
        net_input_shape (numpy.ndarray): The expected 4-dimensional shape of the network.
            The first dimension i.e. the batch_size doesn't really matter.
            Usually the expected shape is [BATCH_SIZE, Height, Width, Channels]
        mean_bgr_255 (numpy.ndarray): 1-dimensional array of means.
            Channel order should be BGR and scale should be [0., 255.]

    Returns:
        caffe.io.Transformer: With all standard transformations set.
    """
    import caffe
    transformer = caffe.io.Transformer({'data': net_input_shape})
    if mean_bgr_255 is not None:
        transformer.set_mean('data', mean_bgr_255)
    transformer.set_transpose('data', (2, 0, 1))
    transformer.set_channel_swap('data', (2, 1, 0))
    transformer.set_raw_scale('data', 255.0)
    return transformer


def caffe_transform_batch(X, net_input_shape, mean_bgr_255=None):
    """Transform a batch of images which were loaded by caffe.io.load_image.

    Transformations:
        - mean subtraction (if mean provided)
        - transposes data to become [Channels x Height x Width]
        - swaps channels to convert RGB to BGR
        - scales the data to [0., 255.]

    Args:
        X (numpy.ndarray):  A batch of images of shape [BATCH_SIZE, Height, Width, RGB-Channels].
            Can be obtained by using `caffe_utils.caffe_load_image`.
    """
    transformer = get_caffe_transformer(net_input_shape, mean_bgr_255)
    transformed_batch = np.array([transformer.preprocess('data', image) for image in X])
    return transformed_batch


def caffe_load_network_with_input_batch(net, X, mean_bgr_255=None, net_input_blob_name='data'):
    """Load the network with the input batch `inplace`.

    Args:
        net (caffe.Network): The network to load the input batch.
        X (numpy.ndarray):  A batch of images of shape [BATCH_SIZE, Height, Width, RGB-Channels].
            Can be obtained by using `caffe_utils.caffe_load_image`.
        mean_bgr_255 (numpy.ndarray): 1-dimensional array of means.
            Channel order should be BGR and scale should be [0., 255.]
        net_input_blob_name (str): The input blob name of the network. Default blob name is "data".

    Returns:
        net: The network is loaded with input inplace but it's returned anyway.
    """
    net_input_shape = net.blobs[net_input_blob_name].data.shape
    transformed_batch = caffe_transform_batch(X, net_input_shape, mean_bgr_255)
    net.blobs[net_input_blob_name].reshape(*transformed_batch.shape)
    net.blobs[net_input_blob_name].data[...] = transformed_batch
    return net
