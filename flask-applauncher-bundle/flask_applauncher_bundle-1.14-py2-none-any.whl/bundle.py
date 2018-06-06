from flask.json import JSONEncoder
import inject
from flask import Flask
import datetime
import applauncher.kernel
from flask_cors import CORS
from applauncher.kernel import Environments, Kernel, KernelReadyEvent, KernelShutdownEvent, Configuration
from werkzeug.serving import make_server


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)


# Just for inject an array as ApiBlueprints
class ApiBlueprints(object):
    pass


class FlaskBundle(object):
    app = None
    srv = None

    def __init__(self):
        self.config_mapping = {
            "flask": {
                "use_debugger": False,
                "port": 3003,
                "host": "0.0.0.0",
                "cors": False,
                "debug": False,
                "secret_key": "cHanGeME"
            }
        }

        self.blueprints = []
        self.injection_bindings = {
            ApiBlueprints: self.blueprints
        }

        self.event_listeners = [
            (KernelReadyEvent, self.kernel_ready),
            (KernelShutdownEvent, self.kernel_shutdown)
        ]

    @inject.params(config=applauncher.kernel.Configuration)
    def start_sever(self, config):
        app = Flask("FlaskServer")

        app.json_encoder = CustomJSONEncoder

        for blueprint in self.blueprints:
            app.register_blueprint(blueprint)

        c = config.flask
        app.secret_key = c.secret_key
        FlaskBundle.app = app
        if c.cors:
            CORS(app)

        if c.debug:
            kernel = inject.instance(Kernel)
            if kernel.environment != Environments.TEST:
                self.srv = make_server(c.host, c.port, app)
                ctx = app.app_context()
                ctx.push()
                self.srv.serve_forever()

    @inject.param("config", Configuration)
    @inject.param("kernel", Kernel)
    def kernel_ready(self, event, config, kernel):
            if config.flask.debug:
                kernel.run_service(self.start_sever)
            else:
                self.start_sever()

    @inject.param("config", Configuration)
    def kernel_shutdown(self, event, config):
        if config.flask.debug:
            self.srv.shutdown()




