# from __future__ import unicode_literals
# import json
# import sys
# import multiprocessing
#
# import gunicorn.app.base
# from gunicorn.six import iteritems
#
# from flask import Flask, request, abort, Response
#
# app = Flask(__name__)
#
#
# class Mapper:
#     __mapper_relation = {}
#
#     @staticmethod
#     def register(cls, value):
#         Mapper.__mapper_relation[cls] = value
#
#     @staticmethod
#     def exist(cls):
#         if cls in Mapper.__mapper_relation:
#             return True
#         return False
#
#     @staticmethod
#     def get_value(cls):
#         return Mapper.__mapper_relation[cls]
#
#
# class AutoFill(type):
#     def __call__(cls, *args, **kwargs):
#         obj = cls.__new__(cls, *args, **kwargs)
#         arg_list = list(args)
#         if Mapper.exist(cls):
#             value = Mapper.get_value(cls)
#             arg_list.append(value)
#         obj.__init__(*arg_list, **kwargs)
#         return obj
#
#
# class StandaloneApplication(gunicorn.app.base.BaseApplication):
#
#     def __init__(self, app, options=None):
#         self.options = options or {}
#         self.application = app
#         super(StandaloneApplication, self).__init__()
#
#     def load_config(self):
#         config = dict([(key, value) for key, value in iteritems(self.options)
#                        if key in self.cfg.settings and value is not None])
#         for key, value in iteritems(config):
#             self.cfg.set(key.lower(), value)
#
#     def load(self):
#         return self.application
#
#
# class Deploy(metaclass=AutoFill):
#
#     def __init__(self, f=None):
#         self.f = f
#
#     @staticmethod
#     def register(func):
#         Mapper.register(Deploy, func)
#
#     @classmethod
#     def run(cls):
#         options = {
#             'bind': '%s:%s' % ('127.0.0.1', '5050'),
#             'workers': cls.num_of_workers(),
#         }
#         StandaloneApplication(app, options).run()
#
#     @classmethod
#     def num_of_workers(cls):
#         workers = int(sys.argv[1]) if len(sys.argv) > 1 or int(sys.argv[1]) < 1 else 1
#         assert workers > 0, ValueError
#         return workers if workers < multiprocessing.cpu_count() * 2 else multiprocessing.cpu_count() * 2
#
#
# @app.route('/_health', methods=['GET'])
# def health():
#     return Response('ok')
#
#
# @app.route('/', methods=['GET', 'POST'])
# def infer():
#     if request.values.get('image_numpy'):
#         d = Deploy()
#         return json.dumps(dict(
#             code=200,
#             data=d.f(request.values.get('image_numpy'))
#         ))
#     else:
#         abort(404)
#
#
# @app.errorhandler(404)
# def page_not_found(error):
#     return json.dumps(dict(
#         code=404,
#         err_msg='Not found, {}'.format(error)
#     ))
#
