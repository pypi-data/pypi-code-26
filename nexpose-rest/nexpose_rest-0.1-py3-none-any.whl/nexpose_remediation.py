from nexpose_rest.nexpose import _GET


def getAssetVulnerabilitySolutions(config, id, vulnerabilityId):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/vulnerabilities/' + str(vulnerabilityId) + '/solution', config, getParameters=getParameters)
    return data
