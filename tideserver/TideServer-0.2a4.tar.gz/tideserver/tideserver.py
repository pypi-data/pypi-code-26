# -*- coding: utf-8 -*-

import os
import time
import logging
from datetime import datetime, timedelta

from flask import Flask, jsonify, request, make_response, g
from flask_restful import Api, Resource
from marshmallow import Schema, fields, post_load

import tidegravity as tg

app = Flask(__name__)
api = Api(app)

CORS_ALLOWED_ORIGIN = os.getenv('CORS_ORIGIN', '*')

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(asctime)s - %(message)s")
log = logging.getLogger(__name__)


@app.before_request
def start_time():
    g.start = time.perf_counter()


@app.after_request
def add_cors_header(response):
    response.headers['Access-Control-Allow-Origin'] = CORS_ALLOWED_ORIGIN
    return response


@app.teardown_request
def execution_time(exception=None):
    diff = time.perf_counter() - g.start
    log.debug("Execution time: %.4f" % diff)
    # print("Execution Time: %.4f" % diff)


def extract_data(df, time_fmt='%Y-%m-%dT%H:%M:%S'):
    """Extracts the relevant fields from pandas DataFrame and packages into a list of dicts"""
    data = []
    for index, series in df.iterrows():
        datum = {"gm": series['gm'], 'gs': series['gs'], 'g0': series['g0'],
                 'ts': index.strftime(time_fmt)}
        data.append(datum)
    return data


def round_time():
    """Retrun a current UTC Datetime object (naive) with seconds truncated to 0"""
    utc = datetime.utcnow()
    return datetime(utc.year, utc.month, utc.day, utc.hour, utc.minute, second=0, microsecond=0)


class TideRequest:
    """
    Simple object to hold parsed Tide Request information, which can be splatted ** into
    a tidegravity method
    """

    def __init__(self, lat, lon, alt=0, n=1, **kwargs):
        self._data = dict(
            lat=lat,
            lon=lon,
            alt=alt,
            n=n,
            increment=kwargs.get('increment', 'min')
        )
        self.delta = kwargs.get('delta', 0)

    def __getitem__(self, item):
        return self._data[item]

    def keys(self):
        return self._data.keys()

    def __len__(self):
        return len(self._data)


class RequestSchema(Schema):
    lat = fields.Float(required=True)
    lon = fields.Float(required=True)
    alt = fields.Float(required=False, default=0)
    n = fields.Integer(required=False, default=1)
    increment = fields.String(required=False, default='min')
    delta = fields.Integer(required=False, default=0)

    @post_load
    def make_obj(self, data):
        return TideRequest(**data)


class TideSeries(Resource):
    def get(self):
        query = {key: request.args[key] for key in request.args}
        errors = RequestSchema().validate(query)
        if errors:
            return make_response(jsonify({"success": False, "msg": errors}))

        params = RequestSchema().load(query).data

        result = tg.solve_point_corr(**params, t0=round_time())
        return jsonify(extract_data(result))

    def post(self):
        if request.json is None:
            return jsonify({"success": False, "msg": "No request body found."})

        errors = RequestSchema().validate(request.json)
        if errors:
            return jsonify({"success": False, "msg": errors})

        params = RequestSchema().load(request.json).data
        result = tg.solve_point_corr(**params, t0=round_time())
        return jsonify(extract_data(result))


class TideDeltaSeries(Resource):
    """Request a tide series from delta minutes ago, to utc time now"""
    def get(self):
        query = {key: request.args[key] for key in request.args}

        params = RequestSchema().load(query).data
        td = timedelta(minutes=params.delta)

        result = tg.solve_point_corr(**params, t0=round_time() - td)
        data = extract_data(result)
        return jsonify(data)


api.add_resource(TideSeries, '/v1/tideseries/')
api.add_resource(TideDeltaSeries, '/v1/tidedelta/')
