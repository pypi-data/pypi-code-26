import json
import requests
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout
import os
import logging

class Event:
    def __init__(self, type, data):
        self.type = type
        self.data = data

class EventService:
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    def __init__(self, location = __location__, crt =  __location__ + "\\client.crt" , pk = __location__ + "\\client.key", server = 'https://localhost:8443'):
        self.log = logging.getLogger(logging.basicConfig(filename=location + "\\file.log",
                                                            level=logging.DEBUG,
                                                            format="%(asctime)s::%(levelname)s::%(message)s",
                                                            datefmt="%Y-%m-%d %H:%M:%S"))
        self.__crt = crt
        self.__pk = pk
        self.__server = server
        self.__headers = {'Content-Type' : 'application/json'}
        self.__timeout = 1

    def __toJson(self, type, data):
        jsonData = {}
        jsonData['type'] = type
        jsonData['data'] = data
        return json.dumps(jsonData)

    def __toEvent(self, j):
        payload = json.loads(j)
        try:
            type = payload['type']
            data = payload['data']
            event = Event(type, data)
            return event
        except KeyError as e:
            self.log.warning('No data retrievable: ' + str(e))
            return None
    
    def __toEvents(self, j):
        payload = json.loads(j)
        events = []
        try:
            for i in range(len(payload)):
                type = payload[i]['type']
                data = payload[i]['data']
                event = Event(type, data)
                events.append(event)
                i+=1
        except KeyError as e:
            self.log.warning('No data retrievable: ' + str(e))
        return events

    def create(self, event):
        self.log.info('Attempting to create event')
        createURL = self.__server + '/events'
        cert = (self.__crt, self.__pk)
        data = self.__toJson(type=event.type, data=event.data)
        self.log.info('Json data:' + data)
        try:
            self.log.info('Trying post')
            requests.post(createURL, data, verify=False, cert=cert, headers=self.__headers, timeout=self.__timeout)
            event = self.__toEvent(data)
            return event
        except ReadTimeout as e:
            self.log.error('Connection timed out: ' + str(e))
        except ConnectionError as e:
            self.log.error('Connection Error: ' + str(e))
            return None
        
    def getId(self, id):
        self.log.info('Attempting to get event by id: ' + id)
        getURL = self.__server + '/events/' + id
        cert = (self.__crt, self.__pk)
        try:
            self.log.info('Trying get by id')
            response = requests.get(getURL, verify=False, cert=cert, headers=self.__headers, timeout=self.__timeout)
            event = self.__toEvent(response.text)
            return event
        except ReadTimeout as e:
            self.log.error('Connection timed out: ' + str(e))
        except ConnectionError as e:
            self.log.error('Connection Error: ' + str(e))
            return None
            
    def getType(self, type=None, page=1, size=2):
        self.log.info('Attempting to get event by type: ' + type)
        if (type != None):
            getURL = self.__server + '/events?type=' + str(type) + '&page=' + str(page) + '&size=' + str(size)
        else:
            getURL = self.__server + '/events?page=' + str(page) + '&size=' + str(size)
        cert = (self.__crt, self.__pk)
        try:
            self.log.info('Trying get by type')
            response = requests.get(getURL, verify=False, cert=cert, headers=self.__headers, timeout=self.__timeout)
            events = self.__toEvents(response.text)
            return events
        except ReadTimeout as e:
            self.log.error('Connection timed out: ' + str(e))
        except ConnectionError as e:
            self.log.error('Connection Error: ' + str(e))
            return None