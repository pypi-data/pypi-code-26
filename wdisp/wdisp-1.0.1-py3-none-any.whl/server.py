
import aiohttp.web
import asyncio
import json
import os.path
import threading
import multiprocessing
import argparse
import time


from . import config
from .service import Image, ImageValues, ImageDB, Messages, MessageStream

ImageNotFound = aiohttp.web.HTTPNotFound()

_db = None

routes = aiohttp.web.RouteTableDef()

def get_image(name):
    im = _db.get_image(name)
    if not im:
        raise ImageNotFound
    return im


@routes.get("/api/preview/{name}")
def preview(request):
    name = request.match_info["name"]
    im = get_image(name)
    return aiohttp.web.Response(body = im.preview, content_type = "image/jpeg")


@routes.get("/api/image/{name}")
def image(request):
    name = request.match_info["name"]
    im = get_image(name)
    return aiohttp.web.Response(body = im.data, content_type = "application/octet-stream")


@routes.post('/api/image')
async def image(request):
    d = await request.content.read()
    data = json.loads(d)
    id = _db.add_image(Image.from_data(data))
    return aiohttp.web.json_response(dict(id = id))


@routes.delete('/api/image/{name}')
def images(request):
    name = request.match_info["name"]
    _db.remove_image(name)
    return aiohttp.web.Response()


@routes.get("/api/images")
def images(request):
    info = [im.info() for im in _db.images.values()]
    return aiohttp.web.json_response({"images": info})


@routes.delete('/api/images')
def images(request):
    _db.remove_all_images()
    return aiohttp.web.Response()

   
@routes.get("/api/image_stream")
async def image_stream(request):
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    
    with _db.message_stream() as stream:
        async for msg in stream:
            await ws.send_json(msg)

    if not ws.closed():
        await ws.close()

    return ws


@routes.get("/api/wait/{time}")
async def wait(request):
    wait_time = int(request.match_info["time"])
    if wait_time == 0:
        wait_time = int(time.time())
    for i in range(10):
        if _db.is_wait_time_ready(wait_time):
            return aiohttp.web.json_response({"ready": True})
        else:
            wait_time = int(time.time())

        await asyncio.sleep(1)
        
    return aiohttp.web.json_response({"ready": False, "time": wait_time})


@routes.post('/api/wait')
def image(request):
    _db.notify_wait_time()
    return aiohttp.web.Response()


@routes.get("/{path:.*}")
async def index(request):
    # This route makes sure that unknown routes are mapped to index.html, so Angular can grab them"""
    path = config.wwwroot() + request.path
    if os.path.isfile(path):
        return  aiohttp.web.FileResponse(path)
    else:
        return aiohttp.web.FileResponse(config.wwwroot() + "/index.html")
    
routes.static("/", config.wwwroot())



def run_server(port = None):
    """Runs the server (blocking)"""

    global _db
    _db = ImageDB()

    if not port:
        port = config.port
    else:
        config.port = port

    app = aiohttp.web.Application()
    app.add_routes(routes)
    aiohttp.web.run_app(app, port = port, shutdown_timeout = 1, print = None)



def run_server_thread(port = None, daemon = True):
    """Runs the server in a new process"""
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        run_server(port)

    t = threading.Thread(target = run, daemon = daemon)
    t.start()
    return t


def run_server_process(port = None, daemon = True):
    """Runs the server in a multiprocessing process"""
    if port:
        config.port = port

    p = multiprocessing.Process(target = run_server, args = (port,), daemon = daemon)
    p.start()
    return p

