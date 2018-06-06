import requests, base64, json
from nexpose_rest.nexpose_administration import *
from nexpose_rest.nexpose_asset import *
from nexpose_rest.nexpose_asset_discovery import *
from nexpose_rest.nexpose_asset_group import *
from nexpose_rest.nexpose_credential import *
from nexpose_rest.nexpose_policy import *
from nexpose_rest.nexpose_policy_override import *
from nexpose_rest.nexpose_remediation import *
from nexpose_rest.nexpose_report import *
from nexpose_rest.nexpose_root import *
from nexpose_rest.nexpose_scan import *
from nexpose_rest.nexpose_scan_engine import *
from nexpose_rest.nexpose_scan_template import *
from nexpose_rest.nexpose_site import *
from nexpose_rest.nexpose_tag import *
from nexpose_rest.nexpose_user import *
from nexpose_rest.nexpose_vulnerability import *
from nexpose_rest.nexpose_vulnerability_check import *
from nexpose_rest.nexpose_vulnerability_exception import *
from nexpose_rest.nexpose_vulnerability_result import *


class Configuration:
    def __init__(self, host, username, password, ssl_verify=True):
        self.host = host
        self.username = username
        self.password = password
        self.ssl_verify = ssl_verify
        self.auth_data = base64.b64encode(self.username + ":" + self.password)


class MalformedResponseError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


class InternalServerError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


class ServiceUnavailableError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


def _GET(url, config, page=1, size=100, getParameters=[]):
    args = '?' + '&'.join(getParameters + ['page=' + str(page - 1),  'size=' + str(size)])
    r = requests.get(config.host + url + args, headers={"Authorization": "Basic %s" % config.auth_data})
    try:
        if r.status_code == 500:
            raise InternalServerError("The server responded with an ERROR Code 500!")
        elif r.status_code == 503:
            raise ServiceUnavailableError("The requested service is not available!")
        res = r.json()
        if "page" in res and "resources" in res and res['page']['totalPages'] > page:
            nested_c, nested_j = _GET(url, config, page=page + 1)
            res['resources'] = res['resources'] + nested_j
        if 'resources' in res:
            return r.status_code, res['resources']
        else:
            return r.status_code, res
    except ValueError as e:
        return -1, MalformedResponseError("Unable to parse Response")


def testConnection(config):
    code, data = _GET('/api/3', config)
    return code == 200
