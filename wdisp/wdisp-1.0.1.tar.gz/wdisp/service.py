
import asyncio
import collections
import base64
import datetime
import numpy as np
import PIL.Image
import io
import time


def _make_preview(image, vmin, vmax, preview_size = (128, 128)):
    """Convert an image to an 8-bit RGB image"""
    channels = 1 if image.ndim == 2 else image.shape[2]
    
    if channels != 1 and channels != 3:
        image = image[0]
    
    if channels == 1 and image.ndim == 3:
        image = np.squeeze(image)

    im = 255 * (image.astype(np.float) - vmin) / (vmax - vmin)

    im = PIL.Image.fromarray(im.astype(np.uint8))
    im = im.resize(preview_size, PIL.Image.BILINEAR)
    data = io.BytesIO()
    im.save(data, format = "jpeg")
    data.seek(0)
    return data.getvalue()


ImageValues = collections.namedtuple("ImageRange", ["vmin", "vmax"])


class Image(object):
    def __init__(self, name, image, values):
        self.id       = 0
        self.name     = name
        self.width    = image.shape[1]
        self.height   = image.shape[0]
        self.channels = 1 if image.ndim == 2 else image.shape[2]
        self.data     = image.tobytes()
        self.dtype    = image.dtype.name
        self.values   = values
        self.time     = datetime.datetime.now()
                
        self.preview = _make_preview(image, values.vmin, values.vmax)

    def info(self):
        return dict(id       = self.id,
                    name     = self.name,
                    width    = self.width,
                    height   = self.height,
                    channels = self.channels,
                    dataType = self.dtype,
                    values   = dict(vmin = self.values.vmin, 
                                    vmax = self.values.vmax),
                    time     = str(self.time))

    @staticmethod
    def from_data(data):
        d = base64.b64decode(data["image"])
        image = np.frombuffer(d, dtype = data["dataType"]).reshape(data["height"], data["width"], data["channels"])
        return Image(data["name"], image, ImageValues(vmin = data["values"]["vmin"], vmax = data["values"]["vmax"]))


    @staticmethod
    def create_data(name, image, values):
        return dict(name     = name,
                    width    = image.shape[1],
                    height   = image.shape[0],
                    channels = 1 if image.ndim == 2 else image.shape[2],
                    dataType = image.dtype.name,
                    values   = dict(vmin = values.vmin, 
                                    vmax = values.vmax),
                    image    = base64.b64encode(image.tobytes()).decode("utf-8"))




class Messages(object):
    @staticmethod
    def add_image(image):
        return dict(type = "add_image",
                    info = image.info())

    @staticmethod
    def remove_image(name):
        return dict(type = "remove_image",
                    name = name)

    @staticmethod
    def remove_all_images():
        return dict(type = "remove_all_images")



class ImageDB(object):
    def __init__(self):
        self._id = 0
        self.images = {}
        self.observer = []
        self.wait_time = 0

        self.notify_wait_time()

    def add_image(self, image):
        image.id = self._next_id()
        self.images[image.name] = image
        self.notify_observer(Messages.add_image(image))
        return image.id
        
    def remove_image(self, name):
        if name in self.images:
            self.images.pop(name)
        self.notify_observer(Messages.remove_image(name))

    def remove_all_images(self):
        self.images.clear()
        self.notify_observer(Messages.remove_all_images())


    def get_image(self, name):
        im = self.images.get(name)
        return im

    def _next_id(self):
        self._id += 1
        return self._id

    def notify_wait_time(self):
        self.wait_time = time.time()

    def is_wait_time_ready(self, time):
        return self.wait_time > time

    def add_observer(self, f):
        self.observer.append(f)
        for im in self.images.values():
            f(Messages.add_image(im))

    def remove_observer(self, f):
        self.observer.remove(f)

    def notify_observer(self, msg):
        for f in self.observer:
            f(msg)

    def message_stream(self):
        return MessageStream(self)




class MessageStream(object):
    def __init__(self, db):
        self._db = db
        self._messages = asyncio.Queue()

    def __enter__(self):
        self._db.add_observer(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._db.remove_observer(self)

    def __call__(self, msg):
        self._messages.put_nowait(msg)

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self._messages.get()




