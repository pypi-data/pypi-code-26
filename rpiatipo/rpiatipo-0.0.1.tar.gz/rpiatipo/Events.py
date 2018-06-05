import json
import requests
import os

class Event:
    def __init__(self, type, data):
        self.type = type
        self.data = data

class EventService:
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    def __init__(self, crt =  __location__ + "\\client.crt" , pk = __location__ + "\\client.key", server = 'https://localhost:8443'):
        self.__crt = crt
        self.__pk = pk
        self.__server = server
        self.__headers = {'Content-Type' : 'application/json'}

    def __toJson(self, type, data):
        jsonData = {}
        jsonData['type'] = type
        jsonData['data'] = data
        return json.dumps(jsonData)

    def __toEvent(self, j):
        payload = json.loads(j)
        type = payload['type']
        data = payload['data']
        event = Event(type, data)
        return event
    
    def __toEvents(self, j):
        payload = json.loads(j)
        events = []
        for i in range(len(payload)):
            type = payload[i]['type']
            data = payload[i]['data']
            event = Event(type, data)
            events.append(event)
            i+=1
        return events

    def create(self, event):
        createURL = self.__server + '/events'
        cert = (self.__crt, self.__pk)
        data = self.__toJson(type=event.type, data=event.data)
        response = requests.post(createURL, data, verify=False, cert=cert, headers=self.__headers)
        payload = self.__toEvent(response.text)
        return payload

    def getId(self, id):
        getURL = self.__server + '/events/' + id
        cert = (self.__crt, self.__pk)
        response = requests.get(getURL, verify=False, cert=cert, headers=self.__headers)
        event = self.__toEvent(response.text)
        return event

    def getType(self, type=None, page=1, size=2):
        if (type != None):
            getURL = self.__server + '/events?type=' + str(type) + '&page=' + str(page) + '&size=' + str(size)
        else:
            getURL = self.__server + '/events?page=' + str(page) + '&size=' + str(size)
        cert = (self.__crt, self.__pk)
        response = requests.get(getURL, verify=False, cert=cert, headers=self.__headers)
        events = self.__toEvents(response.text)
        return events