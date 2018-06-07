import io
import re

from flask import Flask
from PIL import Image
from werkzeug.exceptions import BadRequest

from imgservice.token_serializers import PlainJsonTokenSerializer


class ImgService:

    def __init__(self, name, token_parser=None):
        self.name = name  # Used to configure Flask
        self.token_parser = token_parser or PlainJsonTokenSerializer()
        self._loaders = {}
        self._transforms = {}

    # Configuration --------------------------------------------------

    def define_loader(self, schema, loader):
        self._loaders[schema] = loader

    def define_transform(self, name, transform):
        self._transforms[name] = transform

    # Operation ------------------------------------------------------

    def parse_token(self, token):
        if not token:
            return None
        return self.token_parser.load(token)

    def make_token(self, config):
        return self.token_parser.dump(config)

    def get_image(self, source_url):
        # TODO: we need to allow loaders to return more info too,
        # eg. image ETag from source so we can process caching.

        loader_name = get_url_schema(source_url)
        try:
            loader = self._loaders[loader_name]
        except KeyError:
            raise BadRequest('Unsupported image source: {}'
                             .format(loader_name))
        data = loader(source_url)
        return Image.open(data)

    def apply_image_transforms(self, image_data, config):
        # TODO: we need to allow transforms to return more info too,
        # eg. image type and other headers we might want to set

        for t_name, t_args in config.get('transform', []):
            try:
                t_func = self._transforms[t_name]

            except KeyError:
                raise BadRequest('Unsupported transformation: {}'
                                 .format(t_name))

            image_data = t_func(image_data, **t_args)

        return image_data

    def encode_image(self, image):
        outstream = io.BytesIO()
        image.save(outstream, 'JPEG')
        return outstream.getvalue()

    def build_flask_app(self):
        app = Flask(self.name)

        @app.route('/')
        def home():
            return 'Imgservice 2.0. Nothing to see here.', 200, {
                'content-type': 'text/plain'}

        @app.route('/favicon.ico')
        def favicon():
            # Browsers keep asking for favicon -> prevent errors
            return '', 404

        @app.route('/<token>')
        def process_image(token):
            token_data = self.parse_token(token)

            if token_data is None:
                return 'Hello.', 200

            source_url = token_data['source']
            source = self.get_image(source_url)

            # TODO: handle If-Modified-Since and If-None-Match

            processed = self.apply_image_transforms(source, token_data)
            result = self.encode_image(processed)

            headers = {
                'Content-Type': 'image/jpeg',
                # TODO: 'ETag': 'W/{}'.format(etag),
                # TODO: 'Cache-Control': 'max-age=...'
            }

            return result, 200, headers

        return app

    def get_wsgi_app(self):
        return self.build_flaks_app()


re_url_schema = re.compile(r'^(?P<schema>[a-zA-Z0-9]+)(?:\+[a-zA-Z0-9]+)?://')


def get_url_schema(url):
    """Get schema from a URL.

    Examples:

        'https://...' -> 'https'
        's3://...' -> 's3'
        'foo+http://...' -> 'foo'
    """

    m = re_url_schema.match(url)
    if m is None:
        raise ValueError('Invalid URL (unable to find schema)')
    return m.group('schema')
