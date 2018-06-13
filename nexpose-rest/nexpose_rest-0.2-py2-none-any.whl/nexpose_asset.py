from nexpose_rest.nexpose import _GET


def getAssetServices(config, id):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/services', config, getParameters=getParameters)
    return data


def getAssetServiceWebApplications(config, id, protocol, port):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/services/' + str(protocol) + '/' + str(port) + '/web_applications', config, getParameters=getParameters)
    return data


def getAssetServiceUsers(config, id, protocol, port):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/services/' + str(protocol) + '/' + str(port) + '/users', config, getParameters=getParameters)
    return data


def getAsset(config, id):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '', config, getParameters=getParameters)
    return data


def getAssetSoftware(config, id):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/software', config, getParameters=getParameters)
    return data


def getAssetService(config, id, protocol, port):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/services/' + str(protocol) + '/' + str(port) + '', config, getParameters=getParameters)
    return data


def getOperatingSystem(config, id):
    getParameters=[]
    code, data = _GET('/api/3/operating_systems/' + str(id) + '', config, getParameters=getParameters)
    return data


def getAssetTags(config, id):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/tags', config, getParameters=getParameters)
    return data


def getAssets(config):
    getParameters=[]
    code, data = _GET('/api/3/assets', config, getParameters=getParameters)
    return data


def getAssetUsers(config, id):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/users', config, getParameters=getParameters)
    return data


def getAssetFiles(config, id):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/files', config, getParameters=getParameters)
    return data


def getAssetDatabases(config, id):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/databases', config, getParameters=getParameters)
    return data


def getOperatingSystems(config):
    getParameters=[]
    code, data = _GET('/api/3/operating_systems', config, getParameters=getParameters)
    return data


def getAssetServiceWebApplication(config, id, protocol, port, webApplicationId):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/services/' + str(protocol) + '/' + str(port) + '/web_applications/' + str(webApplicationId) + '', config, getParameters=getParameters)
    return data


def getSoftware(config, id):
    getParameters=[]
    code, data = _GET('/api/3/software/' + str(id) + '', config, getParameters=getParameters)
    return data


def getAssetServiceDatabases(config, id, protocol, port):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/services/' + str(protocol) + '/' + str(port) + '/databases', config, getParameters=getParameters)
    return data


def getSoftwares(config):
    getParameters=[]
    code, data = _GET('/api/3/software', config, getParameters=getParameters)
    return data


def getAssetServiceUserGroups(config, id, protocol, port):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/services/' + str(protocol) + '/' + str(port) + '/user_groups', config, getParameters=getParameters)
    return data


def getAssetUserGroups(config, id):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/user_groups', config, getParameters=getParameters)
    return data


def getAssetServiceConfigurations(config, id, protocol, port):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/services/' + str(protocol) + '/' + str(port) + '/configurations', config, getParameters=getParameters)
    return data
