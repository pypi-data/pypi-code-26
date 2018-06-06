from nexpose_rest.nexpose import _GET


def getPolicyOverrideExpiration(config, id):
    getParameters=[]
    code, data = _GET('/api/3/policy_overrides/' + str(id) + '/expires', config, getParameters=getParameters)
    return data


def getAssetPolicyOverrides(config, id):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(id) + '/policy_overrides', config, getParameters=getParameters)
    return data


def getPolicyOverrides(config):
    getParameters=[]
    code, data = _GET('/api/3/policy_overrides', config, getParameters=getParameters)
    return data


def getPolicyOverride(config, id):
    getParameters=[]
    code, data = _GET('/api/3/policy_overrides/' + str(id) + '', config, getParameters=getParameters)
    return data
