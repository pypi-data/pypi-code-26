from nexpose_rest.nexpose import _GET


def getReportInstances(config, id):
    getParameters=[]
    code, data = _GET('/api/3/reports/' + str(id) + '/history', config, getParameters=getParameters)
    return data


def getReport(config, id):
    getParameters=[]
    code, data = _GET('/api/3/reports/' + str(id) + '', config, getParameters=getParameters)
    return data


def getReports(config):
    getParameters=[]
    code, data = _GET('/api/3/reports', config, getParameters=getParameters)
    return data


def downloadReport(config, id, instance):
    getParameters=[]
    code, data = _GET('/api/3/reports/' + str(id) + '/history/' + str(instance) + '/output', config, getParameters=getParameters)
    return data


def getReportTemplate(config, id):
    getParameters=[]
    code, data = _GET('/api/3/report_templates/' + str(id) + '', config, getParameters=getParameters)
    return data


def getReportInstance(config, id, instance):
    getParameters=[]
    code, data = _GET('/api/3/reports/' + str(id) + '/history/' + str(instance) + '', config, getParameters=getParameters)
    return data


def getReportFormats(config):
    getParameters=[]
    code, data = _GET('/api/3/report_formats', config, getParameters=getParameters)
    return data


def getReportTemplates(config):
    getParameters=[]
    code, data = _GET('/api/3/report_templates', config, getParameters=getParameters)
    return data
