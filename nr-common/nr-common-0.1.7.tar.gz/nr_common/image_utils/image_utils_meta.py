"""."""
import logging
import math
from collections import namedtuple

import cv2
import numpy as np

from nr_common.image_utils import image_utils as image_utils
from nr_common.image_utils import image_utils_cv2 as cv2_utils
from nr_common.image_utils import image_utils_pil as pil_utils

logger = logging.getLogger(__name__)

MetaType = namedtuple(typename="Meta", field_names="scale channel_order shape_order dtype")
META_TYPE_CV2 = MetaType(scale=255, channel_order="BGR", shape_order="HWC", dtype=np.uint8)
META_TYPE_CAFFE = MetaType(scale=1, channel_order="RGB", shape_order="HWC", dtype=np.float32)

ImageWithMeta = namedtuple(typename="ImageWithMeta", field_names="image scale channel_order shape_order dtype")
ImageWithMeta.__doc__ += """.

A namedtuple to store an image array (numpy.ndarray) along with some meta information:
scale (int): The scale of the pixel values.
    - `1` would mean pixel value range of [0-1]
    - `255` would mean pixel value range of [0-255]
channel_order (str): The order of the channels. Currently supported channel_orders are:
    - "RGB"
    - "BGR"
shape_order (str): The order of the axes of the image array. Currently supported shape_orders are:
    - "HWC"
    - "CHW"
dtype (type): The type of the output array. Can be numpy types such as np.float32, np.uint8 or
    standard types such as float or int.
"""


def add_meta_to_image(image, scale=None, channel_order=None, shape_order=None, dtype=None, meta_type=None):
    """Add metadata to an image-ndarray and return an ImageWithMeta object.

    Args:
        image (np.ndarray): The 3D image array.
        scale (int): Either 1 or 255.
            If 1  , then it means the image has pixel values in the range [0, 1]
            If 255, then it means the image has pixel values in the range [0, 255]
        channel_order (str): "RGB" or "BGR". "grayscale" is currently not supported.
            "RGB": It means the image is a color image with channel order RGB
            "BGR": It means the image is a color image with channel order BGR
        shape_oder (str): "HWC". Currently only "HWC" is supported.
            "HWC": It means the 3 dimensions of the image represent Height-Width-Channels.
            "CHW": It means the 3 dimensions of the image represent Channels-Height-Width.
        dtype (str / np.dtype): A string or numpy.dtype that represents the dtype of the image array.
        meta_type (MetaType): (OPTIONAL) A named object that contains some pre-defined set of meta information.
            You can choose some pre-defined meta-types:
                * META_TYPE_CV2
                * META_TYPE_CAFFE
            You can create your own MetaType in case you have some standardized image format and then pass
            it to this function.
                * `my_meta_type = MetaType(scale, channel_order, shape_oder, dtype)`

            NOTE: If you use `meta_type` do not pass other arguments i.e. scale, channel_order, shape_oder, dtype.
    """
    if meta_type:
        scale = meta_type.scale
        channel_order = meta_type.channel_order
        shape_order = meta_type.shape_order
        dtype = meta_type.dtype

    return ImageWithMeta(image=image, scale=scale, channel_order=channel_order, shape_order=shape_order, dtype=dtype)


def load_image(image_filename, scale=255, channel_order="RGB", shape_order="HWC", dtype=np.float32,
               with_meta=False, max_area=None):
    """Load image from filename and transform it to have some pre-defined properties.

    Args:
        image_filename (str): The full path of the image file. The image is expected to be 3D.
        scale (int): The scale of the pixel values.
            - `1` would mean pixel value range of [0-1]
            - `255` would mean pixel value range of [0-255]
        channel_order (str): The order of the channels. Currently supported channel_orders are:
            - "RGB"
            - "BGR"
        shape_order (str): The order of the axes of the image array. Currently supported shape_orders are:
            - "HWC"
            - "CHW"
        with_meta (bool): Whether a simple numpy.ndarray is returned or a namedtuple that contains the image
            and it's meta info is returned.
            - If True, image array with meta-info (ImageWithMeta) is returned
            - If False, image array (numpy.ndarray) is returned
        dtype (type): The type of the output array. Can be numpy types such as np.float32, np.uint8 or
            standard types such as float or int.
        max_area (int): The maximum area i.e. maximum total pixels allowed in the image. If the loaded
            area is greater than max_area then the image is resized keeping the aspect ratio.

    Returns:
        numpy.ndarray: A 3D image array that has the pre-defined properties.
    """
    logger.debug("LOAD IMAGE: scale {} ::: channel_order {} ::: shape_order {} ::: with_meta {} ::: filename {}"
                 .format(scale, channel_order, shape_order, with_meta, image_filename))
    if channel_order == "RGB":
        image = pil_utils.load_image(image_filename)  # RGB, 255, HWC
    elif channel_order == "BGR":
        image = cv2_utils.imread(image_filename)      # BGR, 255, HWC

    # NOTE: This is to make sure that the loaded images doesn't have an
    # area (height * width) greater than max_area.
    # NOTE: This method expects HWC channels & np.uint8 dtype
    if max_area:
        image = image_utils.resize_image_if_exceeds_max_area(image, max_area)

    if scale == 1:
        # The assumption is that image will always be scaled at 255 when it reaches here since all libraries
        # i.e. PIL and OpenCV read images from files at 255 scale.
        image = image / 255.0

    if shape_order == "CHW":
        # TODO: Transform
        raise NotImplementedError

    if image.dtype != dtype:
        image = image.astype(dtype)

    if with_meta is True:
        image = ImageWithMeta(image=image, scale=scale, channel_order=channel_order,
                              shape_order=shape_order, dtype=dtype)

    return image


# TODO: Remove image param
def transform_image(image=None, image_with_meta=None, scale=None, channel_order=None,
                    shape_order=None, dtype=None, meta_type=None, with_meta=False):
    """Transform image or image_with_meta based on some pre-definied properties.

    Args:
        image (numpy.ndarray, ImageWithMeta): ImageWithMeta object that contains the image array and some meta information
            that is to be transformed.
        scale (int): The scale of the pixel values of transformed image.
            - `1` would mean pixel value range of [0-1]
            - `255` would mean pixel value range of [0-255]
        channel_order (str): The order of the channels of the transformed image.
            Currently supported channel_orders are:
            - "RGB" (ImageWithMeta)
            - "BGR" (ImageWithMeta)
            - "REVERSE_CHANNELS" (numpy.ndarray)
        shape_order (str): The order of the axes of the image array.
            Currently supported shape_orders are:
            - "HWC"
            - "CHW"
        with_meta (bool): Whether a simple numpy.ndarray is returned or a namedtuple that contains the image
            and it's meta info is returned.
            - If True, transformed image array with meta-info (ImageWithMeta) is returned
            - If False, transformed image array (numpy.ndarray) is returned
    """
    assert ((image is None and image_with_meta is not None) or
            (image is not None and image_with_meta is None)), "Both image and image_with_meta cannot be None or not None simultaneously."

    assert isinstance(image, (type(None), np.ndarray, np.generic)), (
        "image must be of type NoneType, np.ndarray or np.generic and not {}".format(type(image)))

    assert isinstance(image_with_meta, (type(None), ImageWithMeta)), (
        "image must be of type NoneType or ImageWithMeta and not {}".format(type(image_with_meta)))

    ############################################################################
    # META TYPE
    ############################################################################
    if meta_type:
        scale = meta_type.scale
        channel_order = meta_type.channel_order
        shape_order = meta_type.shape_order
        dtype = meta_type.dtype

    ############################################################################
    # IMAGE WITH META
    ############################################################################
    if image_with_meta is not None:
        logger.debug("TRANSFORM IMAGE: scale {} to {} ::: channel_order {} to {}"
                     .format(image_with_meta.scale, scale, image_with_meta.channel_order, channel_order))
        image = image_with_meta.image

        if (image_with_meta.scale != scale) and scale is not None:
            if scale == 1:
                image = (image / 255.0)  # side effect is that it converts uint8 to float32
            elif scale == 255:
                image = image * 255.0
            else:
                raise ValueError("scale must be either `1` or `255`, instead got {}".format(scale))

        if (image_with_meta.channel_order != channel_order) and channel_order is not None:
            # NOTE: Using `image = image[..., ::-1]` instead of cv2.COLOR_BGR2RGB because it doesn't work with float32.
            if channel_order == "RGB":
                image = image[..., ::-1]
            elif channel_order == "BGR":
                image = image[..., ::-1]
            else:
                raise ValueError("channel_order must be either 'RGB' or 'BGR', instead got {}".format(channel_order))

        if (image_with_meta.shape_order != shape_order) and shape_order is not None:
            # TODO: Swap axes
            raise NotImplementedError

        if (image_with_meta.dtype != dtype) and dtype is not None:
            image = image.astype(dtype)

        if with_meta is True:
            image = ImageWithMeta(image=image, scale=scale, channel_order=channel_order,
                                  shape_order=shape_order, dtype=dtype)

    ############################################################################
    # IMAGE
    ############################################################################
    else:
        if channel_order == "REVERSE_CHANNELS":
            # Make channels [0, 1, 2] into [2, 1, 0]
            image = image[..., ::-1]

    return image


def transform_image_batch(image_batch, input_meta_type, output_meta_type):
    """."""
    output_batch = np.empty(image_batch.shape, dtype=output_meta_type.dtype)
    for i in range(len(image_batch)):
        image_with_meta = add_meta_to_image(image_batch[i], meta_type=input_meta_type)
        output_batch[i] = transform_image(image_with_meta=image_with_meta, meta_type=output_meta_type, with_meta=False)
    return output_batch
