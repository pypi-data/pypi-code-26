from nexpose_rest.nexpose import _GET


def getTags(config, name, type):
    getParameters=[]
    getParameters.append('name=' + name)
    getParameters.append('type=' + type)
    code, data = _GET('/api/3/tags', config, getParameters=getParameters)
    return data


def getTagAssetGroups(config, id):
    getParameters=[]
    code, data = _GET('/api/3/tags/' + str(id) + '/asset_groups', config, getParameters=getParameters)
    return data


def getTaggedSites(config, id):
    getParameters=[]
    code, data = _GET('/api/3/tags/' + str(id) + '/sites', config, getParameters=getParameters)
    return data


def getTag(config, id):
    getParameters=[]
    code, data = _GET('/api/3/tags/' + str(id) + '', config, getParameters=getParameters)
    return data


def getTagSearchCriteria(config, id):
    getParameters=[]
    code, data = _GET('/api/3/tags/' + str(id) + '/search_criteria', config, getParameters=getParameters)
    return data


def getTaggedAssets(config, id):
    getParameters=[]
    code, data = _GET('/api/3/tags/' + str(id) + '/assets', config, getParameters=getParameters)
    return data
