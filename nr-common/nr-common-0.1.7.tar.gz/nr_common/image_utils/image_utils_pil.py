"""."""
import numpy as np
from PIL import Image


def load_image(image_filename):
    """.

    0-255, HWC, RGB
    """
    return np.asarray(Image.open(image_filename))
