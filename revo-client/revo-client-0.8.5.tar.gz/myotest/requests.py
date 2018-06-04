import aiohttp
import async_timeout


REQUEST_TIMEOUT = 30


async def fetch(method, url, *args, **kwargs):
    # sanitize params
    if 'params' in kwargs:
        params = kwargs['params']
        if isinstance(params, dict):
            new_params = {}
            for k, v in params.items():
                if v is not None:
                    new_params[k] = v
            kwargs['params'] = new_params
    with async_timeout.timeout(REQUEST_TIMEOUT):
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, *args, **kwargs) as resp:
                await resp.read()
                return resp


async def get(url, *args, **kwargs):
    return await fetch("GET", url, *args, **kwargs)


async def post(url, *args, **kwargs):
    return await fetch("POST", url, *args, **kwargs)


async def put(url, *args, **kwargs):
    return await fetch("PUT", url, *args, **kwargs)


async def patch(url, *args, **kwargs):
    return await fetch("PATCH", url, *args, **kwargs)


async def delete(url, *args, **kwargs):
    return await fetch("DELETE", url, *args, **kwargs)
