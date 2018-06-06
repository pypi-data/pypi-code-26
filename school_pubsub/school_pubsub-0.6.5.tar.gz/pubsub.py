"""
A module for abstracting pub/sub backends (providing a consistent API across
backends)

Typical usage:

```
pubsub = pubsub.get_backend('backends', 'PubNubBackend', 'some-channel')
pubsub.publish('app.foo', {..})
pubsub.subscribe() # this is a blocking call
```
"""
import importlib, json, os, ast


def get_backend(module, backend_class, channel, appname):
    """Get a pubsub object. e.g.: `get_backend('backends', 'PubNubBackend')`"""
    mod = importlib.import_module(module)
    return getattr(mod, backend_class)(channel, appname)


def publish(backend, key, payload):
    backend.publish(key, payload)


def listen(backend, function_mapper):
    """Process that runs forever listening on configured channel"""
    backend.subscribe(function_mapper)


def get_secret(secret_name, default=None):
    """Returns a docker secret"""
    try:
        return open('/run/secrets/{}'.format(secret_name)).read().rstrip()
    except FileNotFoundError:
        return os.environ.get(secret_name, default)


def normalize(content, as_json=True):
    """
    Take a string, bytestring, dict or even a json object and turn it into a
    pydict
    """
    return ast.literal_eval(content.decode("utf-8"))


def call_mapped_method(message, function_mapper: dict):
    """
    fund method description from function_mapper[message.key]
    and execute function_mapper[message.key](message)

    Where message is a python dict
    """
    if isinstance(message, dict) and not isinstance(message['data'], int):
        data = normalize(message['data'])
        print(type(data))
        event_key = data.get('key')
        task_definition = function_mapper.get(event_key, None)
        if task_definition is not None:
            mod = importlib.import_module(task_definition.get('module'))
            method = task_definition.get('method')
            getattr(mod, method)(data['payload'])
            return data.get('key'), data.get('id')
    return None, None
