"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.server.core.auth.local.models import User
from tornado import web, escape
from collections import defaultdict
import json


class BaseHandler(web.RequestHandler):
    def prepare(self):
        self.set_header("Content-Type", "application/json")

        allow_origin = self.application.pk_settings.get('allow_origin')
        if allow_origin is not None:
            self.set_header("Access-Control-Allow-Origin", allow_origin)
            self.set_header("Access-Control-Allow-Credentials", "true")

        self.json_data = defaultdict(lambda: None)
        try:
            if 'Content-Type' in self.request.headers and \
                    len(self.request.body):
                if self.request.headers["Content-Type"] \
                        .startswith("application/json"):
                    self.json_data.update(escape.json_decode(self.request.body))
                else:
                    raise web.HTTPError(400,
                                        "Content-Type must be application/json")
        except KeyError:
            raise web.HTTPError(400, "Content-Type must be application/json") \
                from None
        except json.decoder.JSONDecodeError:
            raise web.HTTPError(400, "Provided JSON is invalid") from None

        self._db = self.application.db
        self.token = None

        if 'token' in self.json_data:
            if len(self.json_data['token']) == 64:
                self.token = self.json_data['token']
            else:
                raise web.HTTPError(400, "Provided token is not 256 bits long")

    def options(self):
        self.set_header("Access-Control-Allow-Headers",
                        "Content-Type")
        self.set_header("Access-Control-Allow-Methods",
                        "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.set_header("Allow",
                        "HEAD, OPTIONS, GET, POST, PUT, PATCH, DELETE")
        self.set_status(200)

    def get_current_user(self):
        user_id = self.get_secure_cookie("pk_auth_user",
                                         max_age_days=1)

        if not user_id:
            return None

        with self._db as session:
            user = session.query(User).filter_by(id=user_id.decode()).first()

        if user is not None:
            return user.id
        else:
            return None

    def output_json(self, models):
        if type(models) is not list:
            models = [models]

        self.write(json.dumps([m.todict() for m in models]))
