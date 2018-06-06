from nexpose_rest.nexpose import _GET


def getScanEngines(config):
    getParameters=[]
    code, data = _GET('/api/3/scan_engines', config, getParameters=getParameters)
    return data


def getScanEnginePoolSites(config, id):
    getParameters=[]
    code, data = _GET('/api/3/scan_engine_pools/' + str(id) + '/sites', config, getParameters=getParameters)
    return data


def getEnginePool(config, id):
    getParameters=[]
    code, data = _GET('/api/3/scan_engine_pools/' + str(id) + '', config, getParameters=getParameters)
    return data


def getAssignedEnginePools(config, id):
    getParameters=[]
    code, data = _GET('/api/3/scan_engines/' + str(id) + '/scan_engine_pools', config, getParameters=getParameters)
    return data


def getScanEngineScans(config, id):
    getParameters=[]
    code, data = _GET('/api/3/scan_engines/' + str(id) + '/scans', config, getParameters=getParameters)
    return data


def getScanEngine(config, id):
    getParameters=[]
    code, data = _GET('/api/3/scan_engines/' + str(id) + '', config, getParameters=getParameters)
    return data


def getScanEnginePoolScanEngines(config, id):
    getParameters=[]
    code, data = _GET('/api/3/scan_engine_pools/' + str(id) + '/engines', config, getParameters=getParameters)
    return data


def getScanEngineSites(config, id):
    getParameters=[]
    code, data = _GET('/api/3/scan_engines/' + str(id) + '/sites', config, getParameters=getParameters)
    return data


def getScanEnginePools(config):
    getParameters=[]
    code, data = _GET('/api/3/scan_engine_pools', config, getParameters=getParameters)
    return data
