import json
import jsonschema
import requests

from flask import Flask, request, make_response


class gateway_template(object):

    #############################################
    #             Initial config                #
    #############################################
    def __init__(self, network_config, schema_url, childs_config):

        self.schema = self.load_schema(schema_url)
        self.childs = childs_config

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
    #                   Routes                  #
    #############################################
    def create_app(self, debug=False):
        app = Flask(__name__)
        app.debug = debug

        @app.route('/<sub>', methods=['GET'])
        def get(sub):
            return self.get(sub)

        @app.route('/', methods=['POST'])
        def create():
            data = request.get_json()
            return self.create(data)

        @app.route('/<sub>', methods=['PUT'])
        def update(sub):
            new_data = request.get_json()
            return self.update(sub, new_data)

        @app.route('/<sub>', methods=['DELETE'])
        def delete(sub):
            return self.delete(sub)

        @app.route('/<sub>/<type>', methods=['DELETE'])
        def partial_delete(sub, type):
            return self.partial_delete(sub, type)

        @app.route('/', methods=['GET'])
        def search():
            queries = request.args
            return self.search(queries)



        return app



    #############################################
    #               Aux functions               #
    #############################################
    import string
    def id_generator(self, size=16, chars=string.ascii_lowercase + string.digits):
        import random
        return ''.join(random.choice(chars) for _ in range(size))


    def load(self, sub):
        data = {}
        for key in self.childs.keys():
            try:
                r = requests.get(self.childs[key] + '/' + sub, timeout=1)
                if r.status_code == 200:
                    data[key] = r.json()
            except:
                pass
        return data





    #############################################
    #             Module methods                #
    #############################################

    def get(self, sub):
        data = self.load(sub)
        if len(data.keys()) > 0:
            return json.dumps(data)
        else:
            return "No existe", 404


    def create(self, data):
        # Verificamos el esquema
        try:
            jsonschema.validate(data, self.schema)
        except:
            return "No cumple el esquema", 400

        # Creamos un nuevo id que no este utilizado
        sub = self.id_generator()
        while len(self.load(sub)) != 0:
            sub = self.id_generator()

        # Introducimos la informacion en los respectivos microservicios
        outcome = {}
        all_ok = True
        for key in data.keys():
            try:
                r = requests.post(self.childs[key]+'/'+sub, json=data[key], timeout=1)
                outcome[key] = {'status_code': r.status_code, 'text': r.text}
                if r.status_code != 201:
                    all_ok = False
            except:
                all_ok = False

        if all_ok:
            resp = make_response("success", 201)
        else:
            resp = make_response(json.dumps(outcome), 207)

        resp.headers.extend({'resource_id': sub})
        return resp


    def update(self, sub, data):
        outcome = {}
        all_ok = True
        for key in data.keys():
            try:
                r = requests.put(self.childs[key] + '/' + sub, json=data[key], timeout=1)
                outcome[key] = {'status_code': r.status_code, 'text': r.text}
                if r.status_code != 201:
                    all_ok = False
            except:
                all_ok = False

        if all_ok:
            return "success", 201
        else:
            return json.dumps(outcome), 207


    def delete(self, sub):
        outcome = {}
        all_ok = True
        for key in self.childs.keys():
            try:
                r = requests.delete(self.childs[key] + '/' + sub, timeout=1)
                outcome[key] = {'status_code': r.status_code, 'text': r.text}
                if r.status_code != 200:
                    all_ok = False
            except:
                all_ok = False

        if all_ok:
            return "deleted", 200
        else:
            return json.dumps(outcome), 207


    def partial_delete(self, sub, type):
        if type in self.childs.keys():
            r = requests.delete(self.childs[type] + '/' + sub)
            return r.text, r.status_code
        else:
            return "Invalid request", 400


    def search(self, queries):
        # Separamos las queries por microservicios
        map = {}
        for key in queries.keys():
            aux = key.split('.')
            if not(map.has_key(aux[0])):
                map[aux[0]] = ''
            map[aux[0]] = map[aux[0]] + '.'.join(aux[1:]) + '=' + queries[key] + '&'

        # Enviamos las queries a los diferentes microservicios
        matches = {}
        for key in map.keys():
            r = requests.get(self.childs[key] + '?' + map[key])
            if r.status_code == 200:
                bundle = r.json()
                for sub in bundle.keys():
                    if not(matches.has_key(sub)):
                        matches[sub] = {}
                    matches[sub][key] = bundle[sub]

        # Verificamos que ha cumplido con todas las queries
        response = {}
        for sub in matches.keys():
            if not( False in [matches[sub].has_key(key) for key in map.keys()]):
                response[sub] = matches[sub]

        print response
        return json.dumps(response)






    # Reemplazamos un documento por otro
    # def replace(self, sub, data):
    #     try:
    #         jsonschema.validate(data, self.schema)
    #     except:
    #         return "No cumple el esquema", 400
    #
    #     outcome = {}
    #     all_ok = True
    #     for key in self.childs.keys():
    #         if key in data.keys():
    #             r = requests.put(self.childs[key] + '/' + sub, json=data[key])
    #             outcome[key] = {'status_code': r.status_code, 'text': r.text}
    #             if r.status_code != 201:
    #                 all_ok = False
    #         else:
    #             r = requests.delete(self.childs[key] + '/' + sub)
    #             outcome[key] = {'status_code': r.status_code, 'text': r.text}
    #             if r.status_code != 200:
    #                 all_ok = False
    #
    #     if all_ok:
    #         return "success", 201
    #     else:
    #         return json.dumps(outcome), 207


    # Update estricto, si el usuario no existia previamente no lo creo
    # def update(self, sub, new_data):
    # # Comprobamos que ya existia
    #     data = self.load(sub)
    #     if len(data.keys()) == 1:
    #
    #         # Lo actualizamos con la nueva informacion
    #         try:
    #             data.update(new_data)
    #             print data
    #             jsonschema.validate(data, self.schema)
    #         except:
    #             return "No cumple el esquema", 400
    #
    #         outcome = {}
    #         all_ok = True
    #         for key in data.keys():
    #             try:
    #                 r = requests.put(self.childs[key] + '/' + sub, json=data[key], timeout=1)
    #                 outcome[key] = {'status_code': r.status_code, 'text': r.text}
    #                 if r.status_code != 201:
    #                     all_ok = False
    #             except:
    #                 all_ok = False
    #
    #         if all_ok:
    #             return "success", 201
    #         else:
    #             return json.dumps(outcome), 207
    #
    #     else:
    #         return "no hay informacion de esta persona", 404