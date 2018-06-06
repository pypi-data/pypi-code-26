from nexpose_rest.nexpose import _GET


def resources(config):
    getParameters=[]
    code, data = _GET('/api/3', config, getParameters=getParameters)
    return data
