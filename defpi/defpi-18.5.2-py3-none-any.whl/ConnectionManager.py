import logging
from typing import Dict

import re

from defpi.Connection import Connection
from defpi.ConnectionHandler import InterfaceInfo, ConnectionHandler
from defpi.ConnectionHandlerManager import ConnectionHandlerManager
from defpi.Exceptions import ConnectionModificationException
from defpi.TCPConnection import TCPConnection
from defpi.protobufs.Connection_pb2 import ConnectionMessage, ConnectionHandshake, CONNECTED, SUSPENDED, TERMINATED, STARTING


class ConnectionManager:
    logger = logging.getLogger("defpi.ConnectionManager")
    connectionHandlers = dict()  # type: Dict[str, ConnectionHandlerManager]
    interfaceInfo = dict()  # type: Dict[str, InterfaceInfo]

    def __init__(self):
        self.connections = dict()  # type: Dict[str, TCPConnection]

    def handleConnectionMessage(self, message: ConnectionMessage) -> ConnectionHandshake:
        connectionId = message.connectionId
        mode = message.mode
        self.logger.info("Received ConnectionMessage for connection {} ({})".format(connectionId, message.mode))
        self.logger.debug("Received message:\n{}".format(message))

        if mode == ConnectionMessage.CREATE:
            if connectionId not in self.connections:
                return self.createConnection(message)

            self.logger.info("Ignore create-message for already existing connection {}".format(connectionId))
            handshake = ConnectionHandshake()
            handshake.connectionId = connectionId
            handshake.connectionState = CONNECTED
            return handshake
        elif mode == ConnectionMessage.RESUME:
            if connectionId not in self.connections:
                return self.createConnection(message)

            self.connections.get(connectionId).goToResumedState(message.listenPort, message.targetAddress)
            handshake = ConnectionHandshake()
            handshake.connectionId = connectionId
            handshake.connectionState = CONNECTED
            return handshake
        elif mode == ConnectionMessage.SUSPEND:
            self.connections.get(connectionId).goToSuspendedState()
            handshake = ConnectionHandshake()
            handshake.connectionId = connectionId
            handshake.connectionState = SUSPENDED
            return handshake
        elif mode == ConnectionMessage.TERMINATE:
            self.connections.get(connectionId).goToTerminatedState()
            handshake = ConnectionHandshake()
            handshake.connectionId = connectionId
            handshake.connectionState = TERMINATED
            return handshake
        else:
            raise ConnectionModificationException("Invalid connection modification type")

    def createConnection(self, message: ConnectionMessage):
        key = ConnectionManager.handlerKey(message.receiveHash, message.sendHash)
        chf = ConnectionManager.connectionHandlers.get(key)
        info = ConnectionManager.interfaceInfo.get(key)

        if chf is None or info is None:
            self.logger.error("Request for connection with unknown hashes {}, did you register service with "
                              "ConnectionManager.registerHandlers".format(key))
            raise ConnectionModificationException("Unknown connection handling hash: {}".format(key))

        conn = TCPConnection(message.connectionId, message.listenPort, message.targetAddress, info,
                             message.remoteProcessId, message.remoteServiceId, message.remoteInterfaceId)
        self.connections[message.connectionId] = conn
        handshake = ConnectionHandshake()
        handshake.connectionId = message.connectionId
        handshake.connectionState = STARTING
        return handshake

    @staticmethod
    def buildHandlerForConnection(c: Connection, info: InterfaceInfo) -> ConnectionHandler:
        key = ConnectionManager.handlerKey(info.receivesHash, info.sendsHash)
        chf = ConnectionManager.connectionHandlers.get(key)
        methodName = 'build' + ConnectionManager.camelCaps(info.version)

        try:
            return getattr(chf, methodName)(c)
        except Exception as e:
            raise RuntimeError('Error building connection handler {}'.format(e))

    @staticmethod
    def registerConnectionHandlerFactory(handlerClass, connectionHandlerManager: ConnectionHandlerManager):
        if not hasattr(handlerClass, 'info') and type(handlerClass.interfaceInfo) is not InterfaceInfo:
            raise RuntimeError("ConnectionHandler must have the info: InterfaceInfo field available to register")

        info = handlerClass.interfaceInfo
        key = ConnectionManager.handlerKey(info.receivesHash, info.sendsHash)

        ConnectionManager.connectionHandlers[key] = connectionHandlerManager
        ConnectionManager.interfaceInfo[key] = info
        ConnectionManager.logger.debug("Registered {} for type {}".format(connectionHandlerManager, key))


    @staticmethod
    def handlerKey(receiveHash, sendHash):
        return "{}/{}".format(receiveHash, sendHash)

    @staticmethod
    def camelCaps(input: str) -> str:
        camelCase = ' '.join(''.join([w[0].upper(), w[1:].lower()]) for w in input.split())
        return re.sub('[\W_]+', '', camelCase)

    def close(self):
        for key, conn in self.connections.items():
            conn.goToTerminatedState()
