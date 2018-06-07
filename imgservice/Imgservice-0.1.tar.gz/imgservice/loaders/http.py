import io
import logging

import requests
from werkzeug.exceptions import NotFound

logger = logging.getLogger(__name__)


class HttpLoader:

    def __call__(self, name):
        return self.load_image(name)

    def load_image(self, url):
        resp = requests.get(url)
        if not resp.ok:
            # TODO: forward upstream error
            raise NotFound('Unable to load image from source')
        return io.BytesIO(resp.content)
