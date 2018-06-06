from nexpose_rest.nexpose import _GET


def getSiteCredential(config, id, credentialId):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/site_credentials/' + str(credentialId) + '', config, getParameters=getParameters)
    return data


def getSiteDiscoverySearchCriteria(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/discovery_search_criteria', config, getParameters=getParameters)
    return data


def getSiteAssets(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/assets', config, getParameters=getParameters)
    return data


def getSiteSmtpAlert(config, id, alertId):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/alerts/smtp/' + str(alertId) + '', config, getParameters=getParameters)
    return data


def getSiteAlerts(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/alerts', config, getParameters=getParameters)
    return data


def getSiteScanEngine(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/scan_engine', config, getParameters=getParameters)
    return data


def getSiteScanSchedules(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/scan_schedules', config, getParameters=getParameters)
    return data


def getIncludedTargets(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/included_targets', config, getParameters=getParameters)
    return data


def getSite(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '', config, getParameters=getParameters)
    return data


def getExcludedAssetGroups(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/excluded_asset_groups', config, getParameters=getParameters)
    return data


def getWebAuthHTTPHeaders(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/web_authentication/http_headers', config, getParameters=getParameters)
    return data


def getSiteSyslogAlerts(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/alerts/syslog', config, getParameters=getParameters)
    return data


def getSiteUsers(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/users', config, getParameters=getParameters)
    return data


def getWebAuthHtmlForms(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/web_authentication/html_forms', config, getParameters=getParameters)
    return data


def getSiteOrganization(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/organization', config, getParameters=getParameters)
    return data


def getSiteSyslogAlert(config, id, alertId):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/alerts/syslog/' + str(alertId) + '', config, getParameters=getParameters)
    return data


def getExcludedTargets(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/excluded_targets', config, getParameters=getParameters)
    return data


def getSiteCredentials(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/site_credentials', config, getParameters=getParameters)
    return data


def getSiteSharedCredentials(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/shared_credentials', config, getParameters=getParameters)
    return data


def getSiteSnmpAlerts(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/alerts/snmp', config, getParameters=getParameters)
    return data


def getSites(config):
    getParameters=[]
    code, data = _GET('/api/3/sites', config, getParameters=getParameters)
    return data


def getIncludedAssetGroups(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/included_asset_groups', config, getParameters=getParameters)
    return data


def getSiteTags(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/tags', config, getParameters=getParameters)
    return data


def getSiteScanTemplate(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/scan_template', config, getParameters=getParameters)
    return data


def getSiteDiscoveryConnection(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/discovery_connection', config, getParameters=getParameters)
    return data


def getSiteScanSchedule(config, id, scheduleId):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/scan_schedules/' + str(scheduleId) + '', config, getParameters=getParameters)
    return data


def getSiteSmtpAlerts(config, id):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/alerts/smtp', config, getParameters=getParameters)
    return data


def getSiteSnmpAlert(config, id, alertId):
    getParameters=[]
    code, data = _GET('/api/3/sites/' + str(id) + '/alerts/snmp/' + str(alertId) + '', config, getParameters=getParameters)
    return data
