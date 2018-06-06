"""Basic Image Utilities."""
import math

import cv2

import numpy as np


def image_array_to_image_batch(image):
    """Convert image_array to image_batch.

    Args:
        image (ndarray): 3D image array either HWC or CHW

    Returns:
        ndarray: 4D image_batch with batch_size being 1 and NHWC or NCHW format.
    """
    assert image.ndim == 3, "image must be 3D but instead was {}D".format(image.ndim)
    return image[None, :]


def resize_image_if_exceeds_max_area(image, max_area):
    """Resize image if it exceeds max area while maintaining aspect ratio.

    Source: https://stackoverflow.com/questions/33701929/how-to-resize-an-image-in-python-while-retaining-aspect-ratio-given-a-target-s/33702454

    Args:
        image (numpy.ndarray): An image array of HWC shape order and np.uint8 dtype.
        max_area (int): The number of pixels within the image i.e. height * width.

    Returns:
        numpy.ndarray: Resized image maintaining aspect ratio if image_area > max_area.
    """
    img_height, img_width = image.shape[0], image.shape[1]
    img_area = img_height * img_width
    if img_area > max_area:
        aspect_ratio = img_width / img_height
        new_height = int(math.sqrt(max_area / aspect_ratio) + 0.5)
        new_width = int((new_height * aspect_ratio) + 0.5)
        image = cv2.resize(image, (new_width, new_height))
    return image


def img_rotation(cv2_image, rg, fill_mode="constant", cval=0.):
    """."""
    angle = rg
    (h, w) = cv2_image.shape[: 2]
    img_center = (w / 2, h / 2)
    rot_matrix = cv2.getRotationMatrix2D(img_center, angle, 1.0)
    cv2_image = cv2.warpAffine(cv2_image, rot_matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)

    return cv2_image


def img_shift(cv2_image, wrg, hrg, fill_mode="constant", cval=0.):
    """."""
    (h, w) = cv2_image.shape[: 2]

    t_w = wrg * w
    t_h = hrg * h
    t_w = int(t_w)
    t_h = int(t_h)
    transl_matrix = np.float32([[1, 0, t_w], [0, 1, t_h]])
    cv2_image = cv2.warpAffine(cv2_image, transl_matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)

    return cv2_image


def img_horizontal_flip(x):
    """."""
    for i in range(x.shape[2]):
        x[:, :, i] = np.fliplr(x[:, :, i])

    return x


def img_scale(cv2_image, max_scale):
    """."""
    r_scale = max_scale
    r_height = int(np.round(cv2_image.shape[0] * (1 + r_scale)))
    r_width = int(np.round(cv2_image.shape[1] * (1 + r_scale)))
    if r_height <= cv2_image.shape[0]:
        cv2_cropped_image = cv2_image[int((cv2_image.shape[0] - r_height) / 2):
                                      int((cv2_image.shape[0] - r_height) / 2 + r_height),
                                      int((cv2_image.shape[1] - r_width) / 2):
                                      int((cv2_image.shape[1] - r_width) / 2 + r_width)]
        cv2_cropped_image = cv2.resize(cv2_cropped_image, (cv2_image.shape[0], cv2_image.shape[1]))
    else:
        cv2_cropped_image = np.zeros((r_height, r_width, 3), dtype=np.uint8)
        cv2_cropped_image = cv2.copyMakeBorder(cv2_image,
                                               top=int((r_height - cv2_image.shape[0]) / 2),
                                               bottom=int((r_height - cv2_image.shape[0]) / 2),
                                               left=int((r_width - cv2_image.shape[1]) / 2),
                                               right=int((r_width - cv2_image.shape[1]) / 2),
                                               borderType=cv2.BORDER_REPLICATE)
        cv2_cropped_image = cv2.resize(cv2_cropped_image, (cv2_image.shape[0], cv2_image.shape[1]))

    return cv2_cropped_image
