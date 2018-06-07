from base_template import base_template

from flask import request

class backend_template(base_template):

    #############################################
    #               Aux functions               #
    #############################################
    import string
    def id_generator(self, size=16, chars=string.ascii_lowercase + string.digits):
        import random
        return ''.join(random.choice(chars) for _ in range(size))



    #############################################
    #                   Routes                  #
    #############################################
    def create_app(self, debug=False):
        app = super(backend_template, self).create_app()

        @app.route('/<id>', methods=['GET'])
        def get(id):
            queries = request.args
            return self.get(id, queries)

        @app.route('/', methods=['POST'])
        def create():
            queries = request.args
            data = request.get_json()
            return self.create(queries, data)

        @app.route('/<id>', methods=['PUT'])
        def update(id):
            queries = request.args
            data = request.get_json()
            return self.update(id, queries, data)

        @app.route('/<id>', methods=['DELETE'])
        def delete(sub):
            queries = request.args
            return self.delete(id, queries)

        return app


    #############################################
    #             Module methods                #
    #############################################
    def get(self, id, queries):
        return id


    def create(self, queries, data):
        id = self.id_generator()
        return id



    def update(self, id, queries, data):
        return id


    def delete(self, id, queries, data):
        return id

