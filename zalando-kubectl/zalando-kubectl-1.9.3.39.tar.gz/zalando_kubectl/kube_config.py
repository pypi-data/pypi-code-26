import os
import zign.api
import yaml

KUBECONFIG = os.path.expanduser('~/.kube/config')
KUBE_USER = 'zalando-token'


def update(url):
    token = zign.api.get_token('kubectl', ['uid'])
    name = generate_name(url)
    new_config = {
        'apiVersion': 'v1',
        'kind': 'Config',
        'clusters': [{'name': name, 'cluster': {'server': url}}],
        'users': [{'name': KUBE_USER, 'user': {'token': token}}],
        'contexts': [{'name': name, 'context': {'cluster': name, 'user': KUBE_USER}}],
        'current-context': name
    }
    config = insert(new_config)
    write_config(config)
    return config


def update_token():
    token = zign.api.get_token('kubectl', ['uid'])

    config_parts = {
        'users': [{'name': KUBE_USER, 'user': {'token': token}}]
    }
    config = insert(config_parts)
    # Migrate old user names to new name
    for context in config.get('contexts', []):
        if 'zalan_do' in context.get('context', {}).get('user', ''):
            context['context']['user'] = KUBE_USER

    write_config(config)
    return config


def write_config(config):
    os.makedirs(os.path.dirname(KUBECONFIG), exist_ok=True)
    with open(KUBECONFIG, 'w') as fd:
        yaml.safe_dump(config, fd)


def generate_name(url):
    url = url.replace('http://', '')
    url = url.replace('https://', '')
    url = url.replace('.', '_')
    url = url.replace('/', '')
    return url


def read_config():
    try:
        with open(KUBECONFIG, 'r') as fd:
            data = yaml.safe_load(fd)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def insert(new_config):
    config = read_config()
    if 'current-context' in new_config:
        config['current-context'] = new_config['current-context']
    if 'apiVersion' in new_config:
        config['apiVersion'] = new_config['apiVersion']
    if 'kind' in new_config:
        config['kind'] = new_config['kind']

    for key in ['clusters', 'users', 'contexts']:
        if key in new_config:
            for item in new_config[key]:
                insert_key(config, item, key)
    return config


def insert_key(config, item, key):
    if key not in config:
        config[key] = [item]
        return
    for it in config[key]:
        if it['name'] == item['name']:
            it.update(**item)
            return
    config[key].append(item)


def get_current_namespace():
    config = read_config()
    for context in config.get('contexts', []):
        if 'current-context' in config and context['name'] == config['current-context']:
            if 'namespace' in context['context']:
                return context['context']['namespace']
    return 'default'
