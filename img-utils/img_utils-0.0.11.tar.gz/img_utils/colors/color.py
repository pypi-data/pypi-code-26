import colorsys
import random


def random_colors(num_colors, bright=True, darkness=0.7):
    """
    Generate random colors.
    To get visually distinct colors, generate them in HSV space then
    convert to RGB.
    """
    brightness = 1.0 if bright else darkness
    hsv = [(i / num_colors, 1, brightness) for i in range(num_colors)]
    colors = []
    for h, s, v in hsv:
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        colors.append((b, g, r))
    random.shuffle(colors)
    return colors
