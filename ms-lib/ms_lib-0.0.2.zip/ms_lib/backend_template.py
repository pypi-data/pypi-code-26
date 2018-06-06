
from flask import Flask, request

class backend_template(object):

    #############################################
    #             Initial config                #
    #############################################
    def __init__(self, network_config):

        app = self.create_app(debug=True)
        app.run(host=network_config['addr'], port=network_config['port'], threaded=True)


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
        app = Flask(__name__)
        app.debug = debug

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

