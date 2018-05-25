
import urllib
import json
import numpy as np

from . import config
from .service import Image, ImageValues

def do_request(url, method, data = None):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, data = data, method = method))
    except:
        print("Error while showing image")
    return None

def value_range(dtype):
    if   dtype.name == "int8":    return (-128, 127)
    elif dtype.name == "uint8":   return (0, 255)
    elif dtype.name == "int16":   return (-32768, 32767)
    elif dtype.name == "uint16":  return (0, 65535)
    elif dtype.name == "int32":   return (-128, 127)
    elif dtype.name == "uint32":  return (0, 255)
    elif dtype.name == "float32": return (0, 1.0)
    elif dtype.name == "float64": return (0, 1.0)
    raise RuntimeError("Unsupported data type")


def imshow(name, image, vmin = None, vmax = None):
    """Shows an image. vmin and vmax are the minimum and maximum values for mapping or None to use default values."""
    vrange = value_range(image.dtype)
    if vmin is None:
        vmin = vrange[0]
    if vmax is None:
        vmax = vrange[1]

    data = Image.create_data(name, image, ImageValues(vmin = vmin, vmax = vmax))
    do_request(config.url_for("/image"), method = "POST", data = json.dumps(data).encode("utf-8"))


def close(name):
    do_request(config.url_for("/image/" + name), method = "DELETE")

def close_all():
    do_request(config.url_for("/images"), method = "DELETE")


def wait():
    wait_time = 0
    while True:
        resp = do_request(config.url_for("/wait/" + str(wait_time)), method = "GET")
        if resp is None:
            return
        msg = json.loads(resp.read())
        if msg["ready"] == True:
            return
        else:
            time = msg["time"]



def create_test_images():
    print("InitDB")
    imshow("test1", (255*np.random.rand(512, 512, 3)).astype(np.uint8))
    imshow("test2", np.random.rand(1024, 1024, 1))
    imshow("test3", np.random.rand(1024, 1024, 3))