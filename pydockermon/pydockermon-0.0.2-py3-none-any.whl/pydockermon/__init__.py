"""
A python module to interact with ha-dockermon.
This code is released under the terms of the MIT license. See the LICENSE
file for more details.
"""
import requests

class Dockermon:
    """This class is used to interact with ha-dockermon."""

    def __init__(self):
        """Initialize"""

    def listContainers(self, host, port='8126'):
        """Get a list of all containers not in exclude list."""
        BASE = 'http://' + host + ':' + port
        fetchUrl = BASE + '/containers'
        try:
            containers = requests.get(fetchUrl)
        except:
            return False
        else:
            if containers:
                return containers.json()
            else:
                return False

    def getContainerState(self, container, host, port='8126'):
        """Get the state of a container."""
        BASE = 'http://' + host + ':' + port
        fetchUrl = BASE + '/container/' + container
        try:
            containerState = requests.get(fetchUrl)
        except:
            return False
        else:
            if containerState:
                return containerState.json()
            else:
                return False

    def getContainerStats(self, container, host, port='8126'):
        """Get the state of a container."""
        BASE = 'http://' + host + ':' + port
        fetchUrl = BASE + '/container/' + container + '/stats'
        try:
            containerStats = requests.get(fetchUrl)
        except:
            return False
        else:
            if containerStats:
                return containerStats.json()
            else:
                return False

    def startContainer(self, container, host, port='8126'):
        """Start a spesified container"""
        BASE = 'http://' + host + ':' + port
        commandUrl = BASE + '/container/' + container + '/start'
        try:
            runCommand = requests.get(commandUrl)
        except:
            return False
        else:
            if runCommand:
                return True
            else:
                return False

    def stopContainer(self, container, host, port='8126'):
        """Start a spesified container"""
        BASE = 'http://' + host + ':' + port
        commandUrl = BASE + '/container/' + container + '/stop'
        try:
            runCommand = requests.get(commandUrl)
        except:
            return False
        else:
            if runCommand:
                return True
            else:
                return False