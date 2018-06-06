from nexpose_rest.nexpose import _GET


def getUsersWithPrivilege(config, id):
    getParameters=[]
    code, data = _GET('/api/3/privileges/' + str(id) + '/users', config, getParameters=getParameters)
    return data


def getAuthenticationSource(config, id):
    getParameters=[]
    code, data = _GET('/api/3/authentication_sources/' + str(id) + '', config, getParameters=getParameters)
    return data


def getRoleUsers(config, id):
    getParameters=[]
    code, data = _GET('/api/3/roles/' + str(id) + '/users', config, getParameters=getParameters)
    return data


def getAuthenticationSourceUsers(config, id):
    getParameters=[]
    code, data = _GET('/api/3/authentication_sources/' + str(id) + '/users', config, getParameters=getParameters)
    return data


def getRoles(config):
    getParameters=[]
    code, data = _GET('/api/3/roles', config, getParameters=getParameters)
    return data


def getTwoFactorAuthenticationKey(config, id):
    getParameters=[]
    code, data = _GET('/api/3/users/' + str(id) + '/2FA', config, getParameters=getParameters)
    return data


def getUserPrivileges(config, id):
    getParameters=[]
    code, data = _GET('/api/3/users/' + str(id) + '/privileges', config, getParameters=getParameters)
    return data


def getPrivileges(config):
    getParameters=[]
    code, data = _GET('/api/3/privileges', config, getParameters=getParameters)
    return data


def getUserSites(config, id):
    getParameters=[]
    code, data = _GET('/api/3/users/' + str(id) + '/sites', config, getParameters=getParameters)
    return data


def getUsers(config):
    getParameters=[]
    code, data = _GET('/api/3/users', config, getParameters=getParameters)
    return data


def getUser(config, id):
    getParameters=[]
    code, data = _GET('/api/3/users/' + str(id) + '', config, getParameters=getParameters)
    return data


def getAuthenticationSources(config):
    getParameters=[]
    code, data = _GET('/api/3/authentication_sources', config, getParameters=getParameters)
    return data


def getUserAssetGroups(config, id):
    getParameters=[]
    code, data = _GET('/api/3/users/' + str(id) + '/asset_groups', config, getParameters=getParameters)
    return data


def getRole(config, id):
    getParameters=[]
    code, data = _GET('/api/3/roles/' + str(id) + '', config, getParameters=getParameters)
    return data


def getPrivilege(config, id):
    getParameters=[]
    code, data = _GET('/api/3/privileges/' + str(id) + '', config, getParameters=getParameters)
    return data
