import logging
from threading import Condition

from defpi.common.ProtobufMessageSerializer import ProtobufMessageSerializer
from defpi.protobufs.Connection_pb2 import ConnectionHandshake, CONNECTED


class HandShakeMonitor:
    logger = logging.getLogger('defpi.HandShakeMonitor')

    def __init__(self, socket, connectionId):
        self.waitLock = Condition()
        self.socket = socket
        self.connectionId = connectionId
        self.ready = False
        self.serializer = ProtobufMessageSerializer()
        self.closing = False

    def sendHandShake(self, currentState):
        initHandshakeMessage = ConnectionHandshake()
        initHandshakeMessage.connectionId = self.connectionId
        initHandshakeMessage.connectionState = currentState

        self.logger.debug('[{}] - Sending handshake {}'.format(self.connectionId, currentState))

        try:
            msg = self.serializer.serialize(initHandshakeMessage)
            self.socket.send(msg)
        except Exception as e:
            self.logger.info('Exception while sending handshake: {}'.format(e))
            self.close()

    def handleHandShake(self, recvData):
        try:
            handShakeMessage = self.serializer.deserialize(recvData)
        except Exception:
            return False

        if type(handShakeMessage) != ConnectionHandshake:
            return False

        if handShakeMessage.connectionId == self.connectionId:
            self.logger.debug('[{}] - Received acknowledgement: {}'.format(
                self.connectionId, handShakeMessage.connectionState))

            if not self.ready or handShakeMessage.connectionState != CONNECTED:
                self.sendHandShake(CONNECTED)
            else:
                self.logger.debug('[{}] - Not responding to handshake'.format(self.connectionId))

            if handShakeMessage.connectionState == CONNECTED:
                self.logger.info('[{}] - Received connection confirmation, we are ready and release waitLock'.format(
                    self.connectionId))
                self.ready = True
                self.releaseWaitLock()
        else:
            self.logger.warning('[{}] - Invalid Connection ID in Handshake message: {}'.format(
                self.connectionId, handShakeMessage.connectionId))

        return True

    def waitUntilFinished(self, millis):
        if not self.ready:
            with self.waitLock:
                if millis < 1:
                    self.waitLock.wait()
                else:
                    self.waitLock.wait(millis/1000)

    def releaseWaitLock(self):
        with self.waitLock:
            self.waitLock.notifyAll()

    def close(self):
        self.closing = True
        self.releaseWaitLock()
        self.socket.close()
