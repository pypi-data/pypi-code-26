from aiohttp import web
import uuid
import time
from functools import partial

@web.middleware
async def splunk_requests(request, handler):
    request['request_id'] = request.headers.get('x-request-id', str(uuid.uuid4()))
    start_time = time.time()
    await request.app['splunk'].create_event(key="server_log",
                log_type="serverLog",
                name="REQUEST",
                request=request)
    response = await handler(request)
    exec_time = time.time() - start_time

    api = handler
    try:
        while type(api) == partial:
            api = api.keywords['handler']
    except:
        api = handler
    await request.app['splunk'].create_event(
                log_type="serverLog",
                name="RESPONSE",
                request=request,
                event_data={
                    'execution': exec_time,
                    'status_code': response.status,
                    'api': getattr(api, '__name__', '_ModuleError'),
                    'controller': getattr(api, '__module__', '_ModuleError')
                })
    response.headers['x-request-id'] = request['request_id']
    return response
