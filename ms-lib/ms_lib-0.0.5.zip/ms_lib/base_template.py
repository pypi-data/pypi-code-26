from flask import Flask

class base_template(object):

    #############################################
    #             Initial config                #
    #############################################
    def __init__(self, network_config):

        app = self.create_app(debug=True)

        if network_config.has_key('ssl'):
            app.run(host=network_config['addr'], port=network_config['port'], threaded=True, ssl_context=(network_config['ssl']['cert'], network_config['ssl']['key']))
        else:
            app.run(host=network_config['addr'], port=network_config['port'], threaded=True)


    def create_app(self, debug=False):
        app = Flask(__name__)
        app.debug = debug

        return app