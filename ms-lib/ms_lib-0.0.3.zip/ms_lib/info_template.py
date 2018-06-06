
from storage_template import storage_template

from flask import request
import json


class info_template(storage_template):

    #############################################
    #                   Routes                  #
    #############################################
    def create_app(self, debug=False):
        app = super(info_template, self).create_app()

        @app.route('/', methods=['GET'])
        def search():
            queries = request.args
            return self.search(queries)

        return app


    #############################################
    #             Module methods                #
    #############################################
    def search(self, queries):
        filter = {}
        for key in queries:
            value = queries[key]
            filter['data.' + key] = value

        resources = self.storage.load(filter)

        bundle = {}
        for resource in resources:
            bundle[resource['sub']] = resource['data']

        return json.dumps(bundle)

