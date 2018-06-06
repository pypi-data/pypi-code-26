from nexpose_rest.nexpose import _GET


def getPolicies(config, filter, scannedOnly):
    getParameters=[]
    getParameters.append('filter=' + filter)
    getParameters.append('scannedOnly=' + scannedOnly)
    code, data = _GET('/api/3/policies', config, getParameters=getParameters)
    return data


def getPolicyRuleControls(config, policyId, ruleId):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(policyId) + '/rules/' + str(ruleId) + '/controls', config, getParameters=getParameters)
    return data


def getAssetPolicyRulesSummary(config, assetId, policyId):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(assetId) + '/policies/' + str(policyId) + '/rules', config, getParameters=getParameters)
    return data


def getPolicyGroup(config, policyId, groupId):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(policyId) + '/groups/' + str(groupId) + '', config, getParameters=getParameters)
    return data


def getPolicyRule(config, policyId, ruleId):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(policyId) + '/rules/' + str(ruleId) + '', config, getParameters=getParameters)
    return data


def getPolicyRuleAssetResultProof(config, policyId, ruleId, assetId):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(policyId) + '/rules/' + str(ruleId) + '/assets/' + str(assetId) + '/proof', config, getParameters=getParameters)
    return data


def getDisabledPolicyRules(config, policyId):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(policyId) + '/rules/disabled', config, getParameters=getParameters)
    return data


def getPolicyChildren(config, id):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(id) + '/children', config, getParameters=getParameters)
    return data


def getPolicyGroups(config, policyId):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(policyId) + '/groups', config, getParameters=getParameters)
    return data


def getPolicyAssetResults(config, policyId, applicableOnly):
    getParameters=[]
    getParameters.append('applicableOnly=' + applicableOnly)
    code, data = _GET('/api/3/policies/' + str(policyId) + '/assets', config, getParameters=getParameters)
    return data


def getAssetPolicyChildren(config, assetId, policyId):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(assetId) + '/policies/' + str(policyId) + '/children', config, getParameters=getParameters)
    return data


def getPolicyRuleRationale(config, policyId, ruleId):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(policyId) + '/rules/' + str(ruleId) + '/rationale', config, getParameters=getParameters)
    return data


def getPolicyGroupRulesWithAssetAssessment(config, assetId, policyId, groupId):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(assetId) + '/policies/' + str(policyId) + '/groups/' + str(groupId) + '/rules', config, getParameters=getParameters)
    return data


def getPolicyRuleAssetResults(config, policyId, ruleId, applicableOnly):
    getParameters=[]
    getParameters.append('applicableOnly=' + applicableOnly)
    code, data = _GET('/api/3/policies/' + str(policyId) + '/rules/' + str(ruleId) + '/assets', config, getParameters=getParameters)
    return data


def getAssetPolicyGroupChildren(config, assetId, policyId, groupId):
    getParameters=[]
    code, data = _GET('/api/3/assets/' + str(assetId) + '/policies/' + str(policyId) + '/groups/' + str(groupId) + '/children', config, getParameters=getParameters)
    return data


def getPoliciesForAsset(config, assetId, applicableOnly):
    getParameters=[]
    getParameters.append('applicableOnly=' + applicableOnly)
    code, data = _GET('/api/3/assets/' + str(assetId) + '/policies', config, getParameters=getParameters)
    return data


def getPolicyRuleRemediation(config, policyId, ruleId):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(policyId) + '/rules/' + str(ruleId) + '/remediation', config, getParameters=getParameters)
    return data


def getPolicyRules(config, policyId):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(policyId) + '/rules', config, getParameters=getParameters)
    return data


def getPolicySummary(config):
    getParameters=[]
    code, data = _GET('/api/3/policy/summary', config, getParameters=getParameters)
    return data


def getPolicyGroupAssetResult(config, policyId, groupId, assetId):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(policyId) + '/groups/' + str(groupId) + '/assets/' + str(assetId) + '', config, getParameters=getParameters)
    return data


def getPolicyAssetResult(config, policyId, assetId):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(policyId) + '/assets/' + str(assetId) + '', config, getParameters=getParameters)
    return data


def getPolicyGroupAssetResults(config, policyId, groupId, applicableOnly):
    getParameters=[]
    getParameters.append('applicableOnly=' + applicableOnly)
    code, data = _GET('/api/3/policies/' + str(policyId) + '/groups/' + str(groupId) + '/assets', config, getParameters=getParameters)
    return data


def getDescendantPolicyRules(config, policyId, groupId):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(policyId) + '/groups/' + str(groupId) + '/rules', config, getParameters=getParameters)
    return data


def getPolicyRuleAssetResult(config, policyId, ruleId, assetId):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(policyId) + '/rules/' + str(ruleId) + '/assets/' + str(assetId) + '', config, getParameters=getParameters)
    return data


def getPolicyGroupChildren(config, policyId, groupId):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(policyId) + '/groups/' + str(groupId) + '/children', config, getParameters=getParameters)
    return data


def getPolicy(config, policyId):
    getParameters=[]
    code, data = _GET('/api/3/policies/' + str(policyId) + '', config, getParameters=getParameters)
    return data
