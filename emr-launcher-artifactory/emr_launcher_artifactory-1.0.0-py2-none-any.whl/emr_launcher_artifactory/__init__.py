import logging
import requests

logger = logging.getLogger(__name__)


def get_last_modified(path, artifactory_host, verify=True):
    """
        gets the last modified file in a given artifactory path
        Args:
            path - artifactory path
            artifactory_host - which artifactory host to use
        Return:
            str - download url for the latest artifact in the path
    """
    url = 'https://%s/api/storage/%s?lastModified' % (artifactory_host, path)
    resp = requests.get(url, verify=verify)
    if resp.status_code >= 400:
        raise Exception('call to artifactory \'%s\' failed: %s' % (url, resp.text))

    # get the download url
    url = resp.json()['uri']
    resp = requests.get(url, verify=verify)
    if resp.status_code >= 400:
        raise Exception('call to artifactory \'%s\' failed: %s' % (url, resp.text))

    return resp.json()['downloadUri']
