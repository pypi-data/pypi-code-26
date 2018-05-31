import random
import requests
import json

URL = 'http://localhost:8080/api'


def login():
    creds = {
          "password": "admin",
          "rememberMe": True,
          "username": "admin"
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/problem+json'
    }
    rsp = requests.post(URL+'/authenticate', data=json.dumps(creds), headers=headers)
    return rsp.json()

if('__name__' == '__main__'):
    headers = {
        'Content-Type': 'application/json',
            'Accept': 'application/problem+json',
        'Authorization': 'Bearer '+login()['id_token']
    }


def random_number():
    return random.randint(1, 50)


def random_ip():
    return '.'.join(map(str, random.sample(range(0, 255), 4)))


def random_mac():
    return ':'.join(map(lambda x: '%02x' % x, [ 0x00, 0x16, 0x3e,
        random.randint(0x00, 0x7f),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff) ]))


def random_os():
    os = ["Windows10", "Ubuntu x64", "RHEL7", "WindowsServer2016"]
    i = random.randint(0,len(os)-1)
    return os[i]

def random_imageURL():
    images = ['docker.io/ubuntu', 'docker.io/centos', 'docker.io/tensorflow/tensorflow' ]
    i = random.randint(0, len(images) - 1)
    return images[i]

docker_image = {
  "dockerImageType": "TEMPLATE",
  "id": 0,
  "url": "string"
}

task_outputs = {
  "content": "string",
  "id": 0,
  "task": {
    "client": {
      "availableCPUs": 0,
      "availableGBDiskSpace": 0,
      "availableGBRAM": 0,
      "availableGPUs": 0,
      "dateFirstRequest": "2018-03-17",
      "dateLastRequest": "2018-03-17",
      "id": 0,
      "ipAddress": "string",
      "macAddress": "string",
      "operatingSystem": "string"
    },
    "dockerImageUrl": "string",
    "durationMinutes": 0,
    "externalPort": 0,
    "internalPort": 0,
    "id": 0,
    "ioMountPathDst": "string",
    "ioMountPathSrc": "string",
    "name": "string",
    "priority": 0,
    "progress": 0,
    "requiredCPUs": 0,
    "requiredGBDiskSpace": 0,
    "requiredGBRAM": 0,
    "requiredGPUs": 0,
    "taskState": "CREATED",
    "taskZip": "string",
    "taskZipContentType": "string",
    "requiredOperatingSystem": "LINUX",
    "dockerImageType": 'WORKER'
  }
}

clients = {
  "availableCPUs": 0,
  "availableGBDiskSpace": 0,
  "availableGBRAM": 0,
  "availableGPUs": 0,
  "ipAddress": "string",
  "macAddress": "string",
  "operatingSystem": "string"
}


def create_clients(number=10):
    url = URL+'/clients'
    for i in range(number):
        data = {
                  "availableCPUs": random_number(),
                  "availableGBDiskSpace": random_number(),
                  "availableGBRAM": random_number(),
                  "availableGPUs": random_number(),
                  "ipAddress": random_ip(),
                  "macAddress": random_mac(),
                  "operatingSystem": random_os()
                }
        rsp = requests.post(url, data=json.dumps(data), headers=headers)
        print(str(rsp.status_code))

tasks = {
  "client": {
    "availableCPUs": 0,
    "availableGBDiskSpace": 0,
    "availableGBRAM": 0,
    "availableGPUs": 0,
    "dateFirstRequest": "2018-03-17",
    "dateLastRequest": "2018-03-17",
    "id": 0,
    "ipAddress": "string",
    "macAddress": "string",
    "operatingSystem": "string"
  },
  "dockerImageUrl": "string",
  "durationMinutes": 0,
  "externalPort": 0,
  "internalPort": 0,
  "id": 0,
  "ioMountPathDst": "string",
  "ioMountPathSrc": "string",
  "name": "string",
  "priority": 0,
  "progress": 0,
  "requiredCPUs": 0,
  "requiredGBDiskSpace": 0,
  "requiredGBRAM": 0,
  "requiredGPUs": 0,
  "taskState": "CREATED",
  "taskZip": "string",
  "taskZipContentType": "string",
  "requiredOperatingSystem": "LINUX",
  "dockerImageType": 'WORKER'
}

def random_task():
    return { "dockerImageUrl": random_imageURL(),
          "durationMinutes": random_number(),
          "externalPort": random_number(),
          "ioMountPathDst": "string",
          "ioMountPathSrc": "string",
          "name": "string",
          "priority": random_number(),
          "requiredCPUs": random_number(),
          "requiredGBDiskSpace": random_number(),
          "requiredGBRAM": random_number(),
          "requiredGPUs": random_number(),
          "taskState": "CREATED",
          "taskZip": "asdf",
          "taskZipContentType": "string",
          "requiredOperatingSystem": "LINUX"
    }

def create_tasks(number=10):
    url = URL+'/tasks'
    for i in range(number):
        data = random_task()
        rsp = requests.post(url, data=json.dumps(data), headers=headers)
        print(rsp.status_code)