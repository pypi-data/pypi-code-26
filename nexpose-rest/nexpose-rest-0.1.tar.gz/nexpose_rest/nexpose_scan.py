from nexpose_rest.nexpose import _GET


def getSiteScans(config, id, active):
    getParameters=[]
    getParameters.append('active=' + active)
    code, data = _GET('/api/3/sites/' + str(id) + '/scans', config, getParameters=getParameters)
    return data


def getScan(config, id):
    getParameters=[]
    code, data = _GET('/api/3/scans/' + str(id) + '', config, getParameters=getParameters)
    return data


def getScans(config, active):
    getParameters=[]
    getParameters.append('active=' + active)
    code, data = _GET('/api/3/scans', config, getParameters=getParameters)
    return data
