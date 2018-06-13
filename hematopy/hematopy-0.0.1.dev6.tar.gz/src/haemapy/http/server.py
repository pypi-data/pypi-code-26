import os

import click
from apistar import http, ASyncApp, Route
  

def welcome(data: http.RequestData):
    if name is None:
        return {'message': 'Welcome to API Star!'}
    return {'message': 'Welcome to API Star, %s!' % name}


routes = [
    Route('/api/v1/media_objects', method='GET', handler=welcome),
]

app = ASyncApp(routes=routes)


# async def handle(request):
#     name = request.match_info.get('name', "Anonymous")
#     text = "Hello, " + name
#     return web.Response(text=text)

# app = web.Application()

# api = web.Application()
# api.add_routes([web.get('/', handle),
#                 web.get('/{name}', handle)])

# app.add_subapp('/api/v1/', api)


@click.group()
def cli():
    pass

@cli.command('serve')
def cli_serve():
  app.serve(os.environ.get('HOST', 'localhost'), 
            os.environ.get('PORT', 8000), 
            debug=True)