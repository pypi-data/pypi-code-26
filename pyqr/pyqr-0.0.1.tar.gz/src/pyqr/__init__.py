# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'


import qrcode
from pyzbar import pyzbar
from PIL import Image


def decode(file_path):
    data = pyzbar.decode(Image.open(file_path))
    if data:
        return data[0].data.decode('utf-8')


def encode(content, save_path):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    if save_path:
        img.save(save_path)
    return img


def __test():
    encode('HTTPS://QR.ALIPAY.COM/FKX06972YEJOYZ4PSDWCBA', 'demo.png')
    print(decode('demo.png'))


if __name__ == '__main__':
    __test()
