import logging
import pickle
import threading
import traceback

import requests
import time

from defpi.ConnectionManager import ConnectionManager
from defpi.DefPiParameters import generate_defpi_parameters
from defpi.Exceptions import ServiceInvocationException
from defpi.ServiceExecutor import ServiceExecutor
from defpi.common.ProtobufMessageSerializer import ProtobufMessageSerializer
from defpi.common.TCPSocket import TCPSocket
from defpi.protobufs.Service_pb2 import GoToProcessStateMessage, ResumeProcessMessage, SetConfigMessage, RUNNING, \
    SUSPENDED, TERMINATED, ProcessStateUpdateMessage, ErrorMessage
from defpi.protobufs.Connection_pb2 import ConnectionMessage


class ServiceManager:
    _MANAGEMENT_PORT = 4999
    _SOCKET_READ_TIMEOUT_MILLIS = 10000
    _SERVICE_IMPL_TIMEOUT_MILLIS = 5000

    logger = logging.getLogger('defpi.ServiceManager')

    def __init__(self):
        self.connectionManager = ConnectionManager()
        self.logger.info("Start listening thread on {}".format(ServiceManager._MANAGEMENT_PORT))
        self.managementSocket = TCPSocket.asServer(ServiceManager._MANAGEMENT_PORT)
        self.defPiParams = generate_defpi_parameters()
        self.pbSerializer = ProtobufMessageSerializer()
        self.keepThreadAlive = True
        self.executor = ServiceExecutor.getInstance()
        self.managerThread = threading.Thread(target=self.managerThreadFn, args=([]))
        self.managerThread.start()
        self.managedService = None
        self.configured = False

    def managerThreadFn(self):
        while self.keepThreadAlive:
            messageBytes = None
            try:
                messageBytes = self.managementSocket.read(ServiceManager._SOCKET_READ_TIMEOUT_MILLIS)

            except Exception as e:
                self.logger.warning("Socket closed while expecting instruction, re-opening it ({})".format(e))
                self.managementSocket.close()
                self.managementSocket = TCPSocket.asServer(ServiceManager._MANAGEMENT_PORT)

            if messageBytes is None:
                time.sleep(0.1)
                continue

            try:
                msg = self.pbSerializer.deserialize(messageBytes)
                response = self.handleServiceMessage(msg)
            except Exception as e:
                self.logger.error("Exception handling message: {}".format(e))
                traceback.print_exc()
                response = ErrorMessage()
                response.processId = self.defPiParams.getProcessId()
                response.debugInformation = traceback.format_exc()

            try:
                responseArray = self.pbSerializer.serialize(response)
            except Exception as e:
                responseArray = b'Serialization error in servicemanager'
                self.logger.error("Error during serialization of message type {}\n\n{}\n\n{}\n\n".format(response.DESCRIPTOR.name, e, response))
                traceback.print_exc()

            try:
                self.managementSocket.send(responseArray)
            except Exception as e:
                if self.keepThreadAlive:
                    self.logger.warning("Socket closed while sending reply, re-opening it")
                    self.managementSocket.close()
                    self.managementSocket = TCPSocket.asServer(ServiceManager._MANAGEMENT_PORT)
                else:
                    break

    def handleServiceMessage(self, message):
        msgType = type(message)
        if self.managedService is None:
            raise ServiceInvocationException(
                "User service has not instantiated yet, perhaps there is a problem in the constructor")
        elif msgType == GoToProcessStateMessage:
            return self.handleGoToProcessStateMessage(message)
        elif msgType == ResumeProcessMessage:
            return self.handleResumeProcessMessage(message)
        elif msgType == SetConfigMessage:
            return self.handleSetConfigMessage(message)
        elif msgType == ConnectionMessage:
            return self.connectionManager.handleConnectionMessage(message)

    def handleGoToProcessStateMessage(self, message):
        self.logger.debug('Received GoToProcessStateMessage for process {} -> {}'.format(message.processId, message.targetState))
        if message.targetState == RUNNING:
            def futureFn():
                self.managedService.init(None, self.defPiParams)
                self.configured = True
                return self.createProcessStateUpdateMessage(RUNNING)
            future = self.executor.submit(futureFn)
            return future.result(self._SERVICE_IMPL_TIMEOUT_MILLIS / 1000)
        elif message.targetState == SUSPENDED:
            future = self.executor.submit(self.managedService.suspend)
            state = future.result(self._SERVICE_IMPL_TIMEOUT_MILLIS / 1000)
            self.keepThreadAlive = False
            return self.createProcessStateUpdateMessage(SUSPENDED, pickle.dumps(state))
        elif message.targetState == TERMINATED:
            def futureFn():
                try:
                    self.managedService.terminate()
                except Exception as e:
                    self.logger.error("Error while calling terminate")
            future = self.executor.submit(futureFn)
            future.result(self._SERVICE_IMPL_TIMEOUT_MILLIS / 1000)
            self.keepThreadAlive = False
            return self.createProcessStateUpdateMessage(TERMINATED)
        else:
            raise ServiceInvocationException('Invalid target state: {}'.format(message.targetState))

    def handleResumeProcessMessage(self, message):
        self.logger.debug('Received ResumeProcessMessage for process {}'.format(message.processId))
        state = None if not message.stateData else pickle.loads(message.stateData)

        def futureFn():
            self.managedService.resumeFrom(state)
            return self.createProcessStateUpdateMessage(RUNNING)
        future = self.executor.submit(futureFn)
        return future.result(self._SERVICE_IMPL_TIMEOUT_MILLIS / 1000)

    def handleSetConfigMessage(self, message):
        self.logger.debug('Received SetConfigMessage for process {}'.format(message.processId))
        self.logger.debug('Properties to set: {} (update: {})'.format(message.config, message.isUpdate))

        if self.configured != message.isUpdate:
            self.logger.warning("Incongruence detected in message.isUpdate ({}) and service configuration state ({})"
                                .format(message.isUpdate, self.configured))

        def futureFn():
            if not self.configured:
                self.managedService.init(message.config, self.defPiParams)
                self.configured = True
            else:
                self.managedService.modify(message.config)

            return self.createProcessStateUpdateMessage(RUNNING)
        future = self.executor.submit(futureFn)
        return future.result(self._SERVICE_IMPL_TIMEOUT_MILLIS / 1000)

    def createProcessStateUpdateMessage(self, state, data=None):
        msg = ProcessStateUpdateMessage()
        msg.processId = self.defPiParams.getProcessId()
        msg.state = state
        if data is not None:
            msg.stateData = data
        return msg

    def join(self):
        try:
            self.logger.info("Waiting for service thread to stop...")
            if self.managerThread.is_alive():
                self.managerThread.join()
        except InterruptedError:
            self.logger.info("Interuption exception received, stopping...")

    def start(self, service):
        self.managedService = service
        uri = "http://{}:{}{}{}".format(self.defPiParams.getOrchestratorHost(),
                                        self.defPiParams.getOrchestratorPort(),
                                        "/process/trigger/",
                                        self.defPiParams.getProcessId())

        auth_header = {'X-Auth-Token': self.defPiParams.getOrchestratorToken()}
        try:
            r = requests.put(uri, headers=auth_header)

            if r.status_code != 204:
                ServiceManager.logger.error("Unable to request config: "+r.reason)
        except Exception as e:
            ServiceManager.logger.error("Unable to request config: "+str(e))

    def close(self):
        self.keepThreadAlive = False
        if self.managementSocket is not None:
            self.managementSocket.close()

        self.connectionManager.close()
        self.executor.shutdown()
