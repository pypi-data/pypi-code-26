from nexpose_rest.nexpose import _GET


def getSonarQuery(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sonar_queries/' + str(id) + '', config, getParameters=getParameters)
    return data


def getSonarQueryAssets(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sonar_queries/' + str(id) + '/assets', config, getParameters=getParameters)
    return data


def getDiscoveryConnections(config):
    getParameters=[]
    code, data = _GET('/api/3/discovery_connections', config, getParameters=getParameters)
    return data


def getSonarQueries(config):
    getParameters=[]
    code, data = _GET('/api/3/sonar_queries', config, getParameters=getParameters)
    return data


def getDiscoveryConnection(config, id):
    getParameters=[]
    code, data = _GET('/api/3/discovery_connections/' + str(id) + '', config, getParameters=getParameters)
    return data
