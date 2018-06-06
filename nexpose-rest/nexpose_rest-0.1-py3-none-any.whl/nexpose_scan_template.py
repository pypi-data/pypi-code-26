from nexpose_rest.nexpose import _GET


def getScanTemplates(config):
    getParameters=[]
    code, data = _GET('/api/3/scan_templates', config, getParameters=getParameters)
    return data


def getScanTemplate(config, id):
    getParameters=[]
    code, data = _GET('/api/3/scan_templates/' + str(id) + '', config, getParameters=getParameters)
    return data
