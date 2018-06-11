import requests
import justml
import logging
import time

logger = logging.getLogger('justml')

class APIError(Exception):
    def __init__(self, message, status_code, payload):
        super(APIError, self).__init__(self, message)
        self.status_code = status_code
        self.payload = payload

class Client(object):

    api_url = 'https://api.justml.io/v1'

    def __init__(self, api_key=None):
        self.api_key = api_key

    def _call(self, method, path, params=None, files=None, json=None, trials=1):
        func = getattr(requests, method.lower())
        url = '{}{}'.format(self.api_url, path)
        logger.debug('{} {} {}'.format(method, url, json or ''))
        r = func(url,
                 params=params,
                 files=files,
                 json=json,
                 auth=('api', self.api_key or justml.api_key))
        logger.debug('Response: {}'.format(r.text))
        try:
            data = r.json()
        except ValueError:
            data = {}

        if 'warning' in data:
            warnings.warn(data['warning'])

        if r.status_code == 504 and trials < 3:
            logger.debug('Retry.')
            time.sleep(3)
            trials += 1
            return self._call(method, path, params, files, json, trials)

        if r.status_code != 200:
            message = data.get('message', '')
            logger.error('{} {}'.format(r.status_code, message))
            raise APIError(message, r.status_code, data)
        return data

    def list(self, folder):
        return self._call('GET', folder)

    def create(self, folder, **kwargs):
        return self._call('POST', folder, json=kwargs)

    def read(self, folder, id_):
        return self._call('GET', folder + id_)

    def update(self, folder, id_, **kwargs):
        return self._call('PUT', folder + id_, json=kwargs)

    def delete(self, folder, id_):
        return self._call('DELETE', folder + id_)

    def fit(self, folder, id_, filepath):
        res = self.read(folder, id_)
        post = res['training_upload_post']
        f = open(filepath, 'rb')
        try:
            response = requests.post(post['url'], data=post['fields'], files={'file': f})
        finally:
            f.close()
        return response

    def predict(self, folder, id_, filepath):
        f = open(filepath, 'rb')
        try:
            response = self._call('PUT', folder + '%s/predict' % id_, files={'file': f})
        finally:
            f.close()
        return response
