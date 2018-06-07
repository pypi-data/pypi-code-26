from typing import BinaryIO, List, Tuple, Union

import numpy
import pkg_resources
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image


def _make_color_map(image: Image) -> LinearSegmentedColormap:
    image = image.resize((256, image.height))
    colors = (image.getpixel((x, 0)) for x in range(256))
    colors = [[c / 255 for c in color] for color in colors]
    return LinearSegmentedColormap.from_list("from_image", colors)


DOT_IMAGE = Image.open(pkg_resources.resource_filename("heater.resources", "dot.png"))
SCALE_IMAGE = Image.open(pkg_resources.resource_filename("heater.resources", "scale.png"))
SCALE_COLOR_MAP = _make_color_map(SCALE_IMAGE)


def make_heatmap(
        background_file: Union[str, BinaryIO],
        points: List[Tuple[int, int]],
        point_diameter: float = 50,
        point_weight: float = 0.1,
        opacity: float = 0.65,
) -> Image:
    """Generate a heatmap.
    """
    background = Image.open(background_file)
    greymap = _make_greymap(background.width, background.height, points, point_diameter, point_weight)
    heatmap = _change_opacity(_colorize(greymap), opacity)
    return Image.alpha_composite(background.convert("RGBA"), heatmap)


def _colorize(greymap: Image) -> Image:
    return Image.fromarray(SCALE_COLOR_MAP(numpy.array(greymap), bytes=True))


def _make_greymap(
        width: int,
        height: int,
        points: List[Tuple[int, int]],
        point_diameter: float = 50,
        point_weight: float = 0.1,
) -> Image:
    heatmap = Image.new("L", [width, height], color=255)
    point = _make_dot(point_diameter, point_weight)

    for x, y in points:
        position = [
            int(x - point_diameter / 2),
            int(y - point_diameter / 2),
        ]
        heatmap.paste(point, position, mask=point)

    return heatmap


def _make_dot(diameter: float, opacity: float) -> Image:
    dot = DOT_IMAGE.copy().resize([diameter, diameter], resample=Image.ANTIALIAS)
    return _change_opacity(dot, opacity)


def _change_opacity(image: Image, opacity: float) -> Image:
    image_alpha = image.split()[3]
    image.putalpha(image_alpha.point(lambda p: int(p * opacity)))
    return image
