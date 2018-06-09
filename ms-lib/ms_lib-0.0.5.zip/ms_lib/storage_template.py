import json
import jsonschema
import requests

from flask import Flask, request


class storage_template(object):

    #############################################
    #             Initial config                #
    #############################################
    def __init__(self, network_config, schema_url, storage_config):

        self.schema = self.load_schema(schema_url)
        self.storage = self.create_storage(storage_config)

        app = self.create_app(debug=True)
        app.run(host=network_config['addr'], port=network_config['port'], threaded=True)



    #############################################
    #               Load schemas                #
    #############################################
    def load_schema(self, url):
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            exit(1)



    #############################################
    #           Set up the storage              #
    #############################################
    def create_storage(self, storage_config):
        if storage_config['type'] == 'mongodb':
            from storage import mongodb
            storage = mongodb(storage_config)
            return storage
        else:
            exit(1)



    #############################################
    #                   Routes                  #
    #############################################
    def create_app(self, debug=False):
        app = Flask(__name__)
        app.debug = debug

        @app.route('/<sub>', methods=['GET'])
        def get(sub):
            return self.get(sub)

        @app.route('/<sub>', methods=['POST'])
        def create(sub):
            data = request.get_json()
            return self.create(sub, data)

        @app.route('/<sub>', methods=['PUT'])
        def update(sub):
            data = request.get_json()
            return self.update(sub, data)

        @app.route('/<sub>', methods=['DELETE'])
        def delete(sub):
            return self.delete(sub)

        return app


    #############################################
    #             Module methods                #
    #############################################
    def get(self, sub):
        resources = self.storage.load({'sub': sub})
        if len(resources) == 1:
            data = resources[0]['data']
            return json.dumps(data), 200
        else:
            return "El recurso no existe", 404


    def create(self, sub, data):
        # Validamos la informacion recivida frente al esquema
        try:
            jsonschema.validate(data, self.schema)
        except:
            return "El resurso no cumple con el esquema", 400

        # El anadimos el sujeto y lo almacenamos
        resource = {'sub': sub, 'data': data}
        r = self.storage.create(resource)
        if r:
            return 'Success!', 201
        else:
            return 'Ups algo ha ido mal', 400


    def update(self, sub, data):
        # Validamos la informacion recivida frente al esquema
        try:
            jsonschema.validate(data, self.schema)
        except:
            return "El resurso no cumple con el esquema", 400

        # Lo almacenamos
        resource = {'sub': sub, 'data': data}
        r = self.storage.update({'sub': sub}, resource, upsert=True)
        if r:
            return 'Success!', 201
        else:
            return 'Ups algo ha ido mal', 400



    def delete(self, sub):
        r = self.storage.delete({'sub': sub})
        if r > 0:
            return 'Success'
        else:
            return "No se ha podido eliminar el resurso solicitado", 404




    # Forzando a que el recurso existiese previamente
    # def update(self, sub, new_data):
    #     # Verificamos que existe
    #     resources = self.storage.load({'sub': sub})
    #     if len(resources) == 1:
    #         data = resources[0]['data']
    #
    #         # Lo actualizamos con la informacion recivida
    #         try:
    #             data.update(new_data)
    #             jsonschema.validate(data, self.schema)
    #         except:
    #             return "El resurso no cumple con el esquema", 400
    #
    #         # Lo almacenamos
    #         resource = {'sub': sub, 'data': data}
    #         r = self.storage.update({'sub': sub}, resource)
    #         if r:
    #             return 'Success!', 201
    #         else:
    #             return 'Ups algo ha ido mal', 400
    #
    #     else:
    #         return "El recurso no existe", 404


