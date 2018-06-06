from nexpose_rest.nexpose import _GET


def getProperties(config):
    getParameters=[]
    code, data = _GET('/api/3/administration/properties', config, getParameters=getParameters)
    return data


def getLicense(config):
    getParameters=[]
    code, data = _GET('/api/3/administration/license', config, getParameters=getParameters)
    return data


def getSettings(config):
    getParameters=[]
    code, data = _GET('/api/3/administration/settings', config, getParameters=getParameters)
    return data


def getInfo(config):
    getParameters=[]
    code, data = _GET('/api/3/administration/info', config, getParameters=getParameters)
    return data
