import abc

import requests
import six
from requests.auth import HTTPBasicAuth
from urlobject import URLObject

from . import resources


@six.add_metaclass(abc.ABCMeta)
class BaseApiClient(object):
    GET = 'GET'
    POST = 'POST'

    def __init__(self, *args, **kwargs):
        self.logger = self._get_logger()

    @abc.abstractmethod
    def _get_logger(self):
        """
        Return a logger object

        """

    @abc.abstractmethod
    def _raise_http_error(self, *args, **kwargs):
        """
        Raise appropriate exception when HTTP error is occurred

        """

    @abc.abstractmethod
    def _raise_performing_request_error(self, *args, **kwargs):
        """
        Raise appropriate exception when Request cannot be performed

        """

    @abc.abstractmethod
    def _get_auth_string(self):
        """
        Return auth user string
        """

    def request(
            self,
            http_method,
            path,
            params=None,
            data=None,
            json=None,
            base=resources.METADATA_SERVICE_ENDPOINT,
            basic_auth_tuple=None,
            sec_id_for_special_token=None,
            extra_headers=None,
            raw_content=False
    ):
        assert not (basic_auth_tuple and sec_id_for_special_token), 'Only one of these args can be specified'

        if path.startswith('/'):
            path = path[1:]

        retry = False
        auth = None

        if basic_auth_tuple:
            # The basic auth can be used instead of normal Bearer auth
            auth = HTTPBasicAuth(*basic_auth_tuple)
            headers = {}
        else:
            # Normal Bearer auth
            if sec_id_for_special_token:
                assert hasattr(self, 'get_sec_access_token'), 'Method does not exist. Forgot Mixin?'
                # This param is overriding auth with SEC token auth
                headers = {'Authorization': 'Bearer {}'.format(self.get_sec_access_token(sec_id_for_special_token))}
                retry = True
            else:
                # Use user auth
                headers = {'Authorization': self._get_auth_string()}
                retry = False

        url = URLObject(base).add_path(path)
        headers['Content-Type'] = 'application/json'

        if extra_headers:
            headers.update(extra_headers)

        def _request():
            try:
                self.logger.info('Calling metadata service (%s) : %s', http_method, url)
                #print('Request data:')
                #print(data)
                resp_ = requests.request(http_method, url,
                                         params=params, data=data, json=json, headers=headers, auth=auth)

            except requests.RequestException as e_:
                self.logger.info('Outer service request error: {}'.format(e_))
                self._raise_performing_request_error('Error of request performing.: {}'.format(e_))

            return resp_

        resp = _request()
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            self.logger.info(resp.content)

            if retry and resp.status_code in [401, 403]:
                self._retry_occurred()
                # Probably sec_access_token is expired, let's get a new one
                headers = {'Authorization': 'Bearer {}'.format(self.get_sec_access_token(sec_id_for_special_token))}
                # Retry request
                resp = _request()
                try:
                    # print(resp.request.body)
                    # print(resp.content)
                    resp.raise_for_status()
                except requests.HTTPError as e:
                    # This is not access_token expiration, raise exception
                    print(resp.request.body)
                    print(resp.content)
                    self._raise_http_error(resp.status_code, resp.reason)
            else:
                print(resp.request.body)
                print(resp.content)
                self._raise_http_error(resp.status_code, resp.reason)

        except Exception as e:
            # This error should never be happened
            self.logger.info('Unexpected error: {}'.format(e))
            raise

        if not raw_content:
            return resp.json()

        return resp.content

    def _retry_occurred(self):
        """
        This method is overridden for test purposes. By default it's do nothing and don't need to be overridden.
        """
