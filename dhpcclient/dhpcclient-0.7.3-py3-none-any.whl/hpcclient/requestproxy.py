
import requests
import json
import logging

module_logger = logging.getLogger('DHPCLogger')

class RequestProxy(object):
    """
        This class acts as proxy for interacting with the server
    """

    def __init__(self, baseURL):
        """
            Initialize Proxy with the baseURL for requests
        :param baseURL:
        """

        module_logger.info('Initializing proxy')
        self.baseURL = baseURL
        self._headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/problem+json',
            'Authorization': 'Bearer ' + self._login()['id_token']
        }

        module_logger.info('Initialized proxy')
        module_logger.debug('Initialized proxy with %s' % self.__repr__())

    def _login(self):
        creds = {
            "password": "admin",
            "rememberMe": True,
            "username": "admin"
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/problem+json'
        }
        rsp = requests.post(self.baseURL + '/authenticate', data=json.dumps(creds), headers=headers)

        return rsp.json()

    def post(self, path, payload=None):
        """
            Send a POST request to self._baseURL+path
        :param path: Path of the ressource
        :param payload: data to send (json)
        :return: on success: json object, on failure: raises exception
        """

        module_logger.info('POST %s' % path)
        module_logger.debug('POST %s' % str(payload))
        if(path == None or path == ""):
            raise ValueError("No path specified")

        if(payload == None):
            raise ValueError("POST data should have payload")

        response = requests.post(path, data=json.dumps(payload), headers=self._headers)

        if(response.ok):
            return response.json()
        else:
            response.raise_for_status()

    def get(self, path, params=None):
        """
            Send a GET request to self._baseURL+path
        :param path: Ressource to access
        :param params: optional GET parameters
        :return: on success: json object, on failure: raises exception
        """

        module_logger.info('GET %s' % path)
        module_logger.debug('GET parameters are %s' % str(params))

        if(path == None or path == ""):
            raise ValueError("No path specified")

        response = requests.get(path, params=params, headers=self._headers)

        if (response.ok):
            return response.json()
        else:
            response.raise_for_status()

    def put(self, path, payload=None):

        module_logger.info('PUT %s' % path)
        module_logger.debug('PUT %s' % str(payload))

        if (path == None or path == ""):
            raise ValueError("No path specified")

        if (payload == None):
            raise ValueError("PUT data should have payload")

        response = requests.put(path, data=json.dumps(payload), headers=self._headers)

        if (response.ok):
            return response.json()
        else:
            response.raise_for_status()

    def patch(self, path, payload=None):

        module_logger.info('PATCH %s' % path)
        module_logger.debug('PATCH %s' % str(payload))

        if (path == None or path == ""):
            raise ValueError("No path specified")

        if (payload == None):
            raise ValueError("PUT data should have payload")

        response = requests.patch(path, data=json.dumps(payload), headers=self._headers)

        if (response.ok):
            return response.json()
        else:
            response.raise_for_status()

    def delete(self, path):

        module_logger.info('DELETE %s' % path)

        if (path == None or path == ""):
            raise ValueError("No path specified")

        response = requests.delete(path, headers=self._headers)

        if (response.ok):
            return response.json()
        else:
            response.raise_for_status()


    def getTasks(self, filter=""):
        return self.get(self.baseURL+'/tasks'+filter)

    def putTask(self, task):
        return self.put(self.baseURL+'/tasks', task.json_repr())

    def getTask(self, task_id):
        return self.get(self.baseURL+'/tasks/%s' % task_id)

    def postTaskOutput(self, task_logger):
        task_id = task_logger.json_repr()['task']['id']
        return self.post(self.baseURL+'/tasks/%s/task-outputs' % task_id,
                         task_logger.json_repr())

    def putTaskOutput(self, task_logger):
        task_id = task_logger.json_repr()['task']['id']

        return self.put(self.baseURL+'/tasks/%s/task-outputs' % task_id,
                        task_logger.json_repr())

    def patchTaskOutput(self, task_logger):
        task_id = task_logger.json_repr()['task']['id']
        task_output_id = task_logger.id
        return self.patch(
            self.baseURL+'/tasks/%s/task-outputs/%s' % (task_id, task_output_id),
            payload={'id': task_output_id, 'content': task_logger.read(), 'task': task_logger.json_repr()['task']})

    def postClient(self, client):
        return self.post(self.baseURL+'/clients', payload=client.json_repr())

    def __repr__(self):
        return json.dumps(self.json_repr())

    def json_repr(self):
        return {
            'baseURL': self.baseURL,
            'headers': self._headers
        }





