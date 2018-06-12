import numpy as np
from PIL import Image, ImageDraw, ImageFont

def _get_rect(x, y, width, height, angle):
    rect = np.array([(0, 0), (width, 0), (width, height), (0, height), (0, 0)])
    theta = (np.pi / 180.0) * angle
    R = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta), np.cos(theta)]])
    return np.dot(rect, R) + np.array([x, y])

def rect(pallete, x, y, w, h, angle=0, color=0):
    _rect = _get_rect(x, y, w, h, angle)
    img = Image.fromarray(pallete)
    draw = ImageDraw.Draw(img)
    draw.polygon([tuple(p) for p in _rect], fill=color)
    pallete[:, :, :] = np.asarray(img)


def line(pallete, x1, y1, x2, y2, color=0):
    img = Image.fromarray(pallete)
    draw = ImageDraw.Draw(img)
    draw.line((x1, y1, x2, y2), fill=color)
    pallete[:, :, :] = np.asarray(img)


def image(pallete, x, y, img):
    bg = Image.fromarray(pallete)
    if isinstance(img, str):
        _img = Image.open(img)
        bg.paste(_img, (x, y), _img)
    else:
        raise ValueError('unknown img type.')
    pallete[:, :, :] = np.asarray(bg)

def text(pallete, x, y, text, font=None, size=None, color=0):
    img = Image.fromarray(pallete)
    draw = ImageDraw.Draw(img)
    if font and size:
        _font = ImageFont.truetype(font, size)
    else:
        _font = None
    draw.text((x, y), text, font=_font, fill=color)
    pallete[:, :, :] = np.asarray(img)
