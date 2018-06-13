from nexpose_rest.nexpose import _GET


def getAssetGroup(config, id):
    getParameters=[]
    code, data = _GET('/api/3/asset_groups/' + str(id) + '', config, getParameters=getParameters)
    return data


def getAssetGroupTags(config, id):
    getParameters=[]
    code, data = _GET('/api/3/asset_groups/' + str(id) + '/tags', config, getParameters=getParameters)
    return data


def getAssetGroupUsers(config, id):
    getParameters=[]
    code, data = _GET('/api/3/asset_groups/' + str(id) + '/users', config, getParameters=getParameters)
    return data


def getAssetGroupAssets(config, id):
    getParameters=[]
    code, data = _GET('/api/3/asset_groups/' + str(id) + '/assets', config, getParameters=getParameters)
    return data


def getAssetGroups(config, type=None, name=None):
    getParameters=[]
    if type is not None:
        getParameters.append('type=' + type)
    if name is not None:
        getParameters.append('name=' + name)
    code, data = _GET('/api/3/asset_groups', config, getParameters=getParameters)
    return data


def getAssetGroupSearchCriteria(config, id):
    getParameters=[]
    code, data = _GET('/api/3/asset_groups/' + str(id) + '/search_criteria', config, getParameters=getParameters)
    return data
