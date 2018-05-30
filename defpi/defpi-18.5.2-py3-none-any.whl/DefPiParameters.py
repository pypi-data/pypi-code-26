import os


def generate_defpi_parameters():
    """Read defpi parameters from docker environments vars"""
    orchestratorHost = os.environ.get('ORCHESTRATOR_HOST') or 'null'
    orchestratorPort = os.environ.get('ORCHESTRATOR_PORT') or 4999
    orchestratorToken = os.environ.get('ORCHESTRATOR_TOKEN') or 'null'
    processId = os.environ.get('PROCESS_ID') or 'null'
    userId = os.environ.get('USER_ID') or 'null'
    username = os.environ.get('USER_NAME') or 'null'
    userEmail = os.environ.get('USER_EMAIL') or 'null'
    return DefPiParameters(orchestratorHost, orchestratorPort, orchestratorToken,
                           processId, userId, username, userEmail)


class DefPiParameters(object):

    def __init__(self, orchestratorHost, orchestratorPort, orchestratorToken,
                 processId, userId, username, userEmail):
        self.ORCHESTRATOR_HOST = orchestratorHost
        self.ORCHESTRATOR_PORT = orchestratorPort
        self.ORCHESTRATOR_TOKEN = orchestratorToken
        self.PROCESS_ID = processId
        self.USER_ID = userId
        self.USER_NAME = username
        self.USER_EMAIL = userEmail

    def getOrchestratorHost(self):
        return self.ORCHESTRATOR_HOST

    def getOrchestratorPort(self):
        return self.ORCHESTRATOR_PORT

    def getOrchestratorToken(self):
        return self.ORCHESTRATOR_TOKEN

    def getProcessId(self):
        return self.PROCESS_ID

    def getUserId(self):
        return self.USER_ID

    def getUsername(self):
        return self.USER_NAME

    def getUserEmail(self):
        return self.USER_EMAIL

    def __str__(self):
        return "DefPiParameters [orchestratorHost=" + self.ORCHESTRATOR_HOST + ", orchestratorPort=" \
               + str(self.ORCHESTRATOR_PORT) + ", orchestratorToken=" + self.ORCHESTRATOR_TOKEN + ", processId=" \
               + self.PROCESS_ID + ", userId=" + self.USER_ID + ", username=" + self.USER_NAME + ", userEmail=" \
               + self.USER_EMAIL + "]"
