import io

from PIL import Image


def crop_image(image, width=None, height=None):
    _validate_int_argument(width, (1, 4000))
    _validate_int_argument(width, (1, 4000))

    # Retrieve from S3 to memory
    # TODO: use a default image (configured) if not found
    input_stream = io.BytesIO()

    if width is None:
        width = image.width

    if height is None:
        height = image.height

    crop_rectangle = get_crop_rectangle(image.width, image.height, width, height)

    image = image.crop(crop_rectangle)
    image = image.resize((width, height), Image.ANTIALIAS)

    # TODO: this can be done in a separate transform
    if image.mode != 'RGB':
        image = image.convert('RGB')

    return image

    # TODO: make sure we rotate images correctly

    # TODO: strip all EXIF metadata
    # TODO: set compression options and stuff


def _validate_int_argument(value, bounds):
    minval, maxval = bounds

    if value is None:
        return None

    try:
        intval = int(value)

    except ValueError:
        raise ValueError('Parameter must be an integer')

    if not (minval <= intval <= maxval):
        raise ValueError('Parameter out of bounds ({}, {})'
                         .format(minval, maxval))

    return intval


def get_crop_rectangle(img_width, img_height, crop_width, crop_height):
    min_ratio = min((img_width / crop_width, img_height / crop_height))
    crop_width *= min_ratio
    crop_height *= min_ratio
    horiz_margin = (img_width - crop_width) / 2
    vert_margin = (img_height - crop_height) / 2
    return (
        horiz_margin,
        vert_margin,
        horiz_margin + crop_width,
        vert_margin + crop_height)
