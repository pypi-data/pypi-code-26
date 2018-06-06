from nexpose_rest.nexpose import _GET


def getSharedCredential(config, id):
    getParameters=[]
    code, data = _GET('/api/3/shared_credentials/' + str(id) + '', config, getParameters=getParameters)
    return data


def getSharedCredentials(config):
    getParameters=[]
    code, data = _GET('/api/3/shared_credentials', config, getParameters=getParameters)
    return data
