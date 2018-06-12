"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from tornado import web


class WebHandler(web.RequestHandler):
    def get(self):
        self.render('../site/index.html')
