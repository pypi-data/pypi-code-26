import datetime
from datetime import timezone
import time
import json
from uuid import UUID
import os
import asyncio
from aiohttp import ClientSession
import inspect
from aiohttp.web_request import Request, BaseRequest

class SplunkLoggingClient(object):
    _key = None
    _auth_key = "Splunk "
    _url = None
    _connection = None

    def __init__(self, settings={}, *args, **kwargs):
        self._auth_key += settings.get('HEC_TOKEN', '')
        self._url = 'https://' if settings.get('ENABLE_SSL') else 'http://'
        self._url += settings.get('ADDRESS') + ":" + \
            settings.get('HEC_PORT') + \
            '/services/collector/event'
        self._source = settings.get('SOURCE')
        self._index = settings.get("INDEX")
        self._session = ClientSession(loop=kwargs.get('loop', asyncio.get_event_loop()))

    async def create_event(self, *args, **kwargs):
        event_time = str(kwargs.get('event_time', datetime.datetime.utcnow().replace(tzinfo=timezone.utc)).timestamp())
        request = kwargs.get('request', None)
        event_data = await self.format_event_data(kwargs.get('event_data'))
        request_data = await self.format_request(kwargs.get('request', self._find_request()))
        payload = {
            'time': event_time,
            'sourcetype': kwargs.get('log_type', 'serverLog'),
            'event': {
                'request': request_data,
                'eventData': event_data,
                'event': kwargs.get('name', 'EVENT'),
            }
        }
        if self._source:
            payload['source'] = self._source
        if self._index:
            payload['index'] = self._index
        await self.send_to_splunk(payload)
        return True
 
    async def format_event_data(self, obj):
        if obj is None:
            return {}
        cleaned_object_data = {}
        if 'to_json' in dir(obj):
            for k, v in obj.to_json().items():
                cleaned_object_data[k] = v

        elif isinstance(obj, dict):
            for key, value in obj.items():
                if type(value) is datetime.datetime:
                    cleaned_object_data[key] = value.strftime('%m/%d/%Y %H:%M:%S')
                elif type(value) is UUID:
                    cleaned_object_data[key] = str(value)
                else:
                    cleaned_object_data[key] = value
        else:
            for oa in [x for x in obj.__dict__ if not x.startswith('_')]:
                if type(getattr(obj, oa)) is datetime.datetime:
                    cleaned_object_data[oa] = getattr(obj, oa).strftime('%m/%d/%Y %H:%M:%S')
                elif type(getattr(obj, oa)) is UUID:
                    cleaned_object_data[oa] = str(getattr(obj, oa))
                else:
                    cleaned_object_data[oa] = getattr(obj, oa)
        return cleaned_object_data

    def _find_request(self):
        request = None
        frames = inspect.stack()
        for frame in [frames[i].frame for i in range(len(frames)-1, 0, -1)]:
            if ('request' in frame.f_locals.keys() 
                and type(frame.f_locals.get('request')) == Request 
                and type(frame.f_locals.get('request')) != BaseRequest
                ):
                request = frame.f_locals.get('request')
                break
        return request

    async def format_request(self, request):
        """ Format the request to JSON. """
        if request == None:
            return {}
        else:
            request_data = {
                'path': request.path,
                'host': request.host,
                'query': dict(request.query),
                'method': request.method,
                'content_type': request.content_type,
                'client_ip': request.remote,
                'scheme': request.scheme,
                'headers': dict(request.headers),
                'params': {}
            }
            if request.get('request_id'):
                request_data['id'] = request.get('request_id')
            if request.method is not "GET":
                post_data = await request.post()
                for x,y in post_data:
                    request_data['params'][x] = y
            if request.match_info:
                request_data['params'].update(request.match_info)
            return request_data

    async def send_to_splunk(self, payload):
        async with self._session.post(self._url,\
                      headers={'Authorization': self._auth_key},\
                      data=json.dumps(payload)) as response:
            if response.status > 299:
                text = await response.text()
                print('error sending splunk event to http collector: {0}'.format(
                    text))
