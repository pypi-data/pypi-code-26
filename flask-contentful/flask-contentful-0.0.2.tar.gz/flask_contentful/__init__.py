import contentful

from flask import current_app
from typing import NamedTuple

from .filters import markdown_filter

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class ContentType(NamedTuple):
    id: str
    name: str


class Contentful(object):
    def __init__(self, app=None) -> None:
        self.app = app
        if app is not None:
            self.init_app(app)
            self.load_filters(app)

    def init_app(self, app):
        pass

    def load_filters(self, app):
        app.jinja_env.filters['markdown'] = markdown_filter

    @property
    def _client(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'contentful_client'):
                ctx.contentful_client = contentful.Client(
                    current_app.config['CONTENTFUL_SPACE'],
                    current_app.config['CONTENTFUL_ACCESS_TOKEN']
                )
            return ctx.contentful_client

    @property
    def content_types(self):
        return [ContentType(ct.id, ct.name) for ct in self._client.content_types()]

    @property
    def client(self):
        return self._client
