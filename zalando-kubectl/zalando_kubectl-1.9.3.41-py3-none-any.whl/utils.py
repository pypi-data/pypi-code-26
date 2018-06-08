import zign.api


def auth_headers():
    token = zign.api.get_token('kubectl', ['uid'])
    return {'Authorization': 'Bearer {}'.format(token)}
