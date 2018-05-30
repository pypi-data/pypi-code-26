import logging
import traceback
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
from threading import Condition

import time

from defpi.Connection import Connection
from defpi.ConnectionHandler import InterfaceInfo, ConnectionHandler
from defpi.Exceptions import UnsupportedDataTypeException
from defpi.HandShakeMonitor import HandShakeMonitor
from defpi.HeartBeatMonitor import HeartBeatMonitor
from defpi.ServiceExecutor import ServiceExecutor
from defpi.common.TCPSocket import TCPSocket
from defpi.protobufs.Connection_pb2 import STARTING, CONNECTED, INTERRUPTED, SUSPENDED, TERMINATED
from defpi.common.ProtobufMessageSerializer import ProtobufMessageSerializer


class TCPConnection(Connection):
    remoteProcessId = None
    remoteServiceId = None
    remoteInterfaceId = None

    def __enter__(self): return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __init__(self, connectionId: str, port: int, targetAddress: str, info: InterfaceInfo,
                 remoteProcessId: str, remoteServiceId: str, remoteInterfaceId: str):

        self.serviceExecutor = ServiceExecutor.getInstance()
        self.userMessageSerializer = None  # type: ProtobufMessageSerializer
        self.info = None  # type: InterfaceInfo

        self.serviceHandler = None  # type: ConnectionHandler

        self.socket = None  # type: TCPSocket
        self.heartBeatMonitor = None  # type: HeartBeatMonitor
        self.handShakeMonitor = None  # type: HandShakeMonitor

        self.logger = logging.getLogger("defpi.TCPConnection - {}".format('server' if not targetAddress else 'client'))

        self.connectionExecutor = ThreadPoolExecutor(max_workers=6)
        self.keepRunning = True
        self.state = STARTING
        self.connectionId = connectionId
        self.port = port
        self.targetAddress = targetAddress
        self.info = info
        self.remoteProcessId = remoteProcessId
        self.remoteServiceId = remoteServiceId
        self.remoteInterfaceId = remoteInterfaceId
        self.connectionLock = Condition()
        self.closeLock = Condition()
        self.internalQueue = Queue()

        self.userMessageSerializer = ProtobufMessageSerializer(True)
        self.mqFuture = self.connectionExecutor.submit(self.messageQueue)
        self.srFuture = self.connectionExecutor.submit(self.socketReader)

    def isConnected(self):
        return self.state == CONNECTED and self.handShakeMonitor is not None and self.handShakeMonitor.ready

    def send(self, message):
        if message is None:
            self.logger.warning("Send method was called with None message, ignoring..")
            return

        if not self.isConnected():
            self.logger.warning("Unable to send when connection state is {}!".format(self.state))

        try:
            data = self.userMessageSerializer.serialize(message)
        except Exception as e:
            self.logger.error("Error while serializing message, not sending message. {}".format(e))
            raise UnsupportedDataTypeException("Error serializing message: {}".format(str(e)))

        try:
            self.socket.send(data)
        except Exception as e:
            self.logger.warning("Failed to send message through socket, goto {}".format(INTERRUPTED))
            raise e

    def getState(self): return self.state

    def handleMessage(self, msg):
        try:
            with self.connectionLock:
                if self.serviceHandler is None:
                    try:
                        self.logger.warning("Received message {} before connection is established. Hold..".format(msg))
                        self.connectionLock.wait()
                        self.logger.warning("continue..")
                    except InterruptedError as e:
                        self.logger.warning("Interrupt: {}".format(e))

            message, msgTypeName = self.userMessageSerializer.deserialize(msg, True)
            try:
                method = getattr(self.serviceHandler, "handle{}Message".format(msgTypeName))
            except AttributeError:
                self.logger.warning("Did not find handle method for {}".format(msgTypeName))
                return

            try:
                method(message)
            except Exception as e:
                self.logger.error("Exception while invoking handle{}Message ({})".format(msgTypeName, e))
        except Exception as msg:
            self.logger.warning("Received unknown message: {}. Ignoring...".format(msg))
            traceback.print_exc()

    def releaseWaitLock(self):
        with self.connectionLock:
            self.connectionLock.notify_all()

    def waitUntilConnected(self, millis=None):
        if self.isConnected():
            return

        with self.connectionLock:
            self.connectionLock.wait(millis)

        if not self.isConnected():
            raise BrokenPipeError

    def goToConnectedState(self):
        self.logger.info("Going from {} to {}".format(self.state, CONNECTED))
        previousState = self.state
        self.state = CONNECTED

        if previousState == CONNECTED:
            self.logger.debug("Ignoring goToConnected, already connected")
        elif previousState == STARTING:
            def futureFn():
                self.serviceHandler = ConnectionManager.buildHandlerForConnection(self, self.info)
            self.serviceExecutor.submit(futureFn)
        elif previousState == INTERRUPTED:
            self.logger.debug("Executing resumeAfterInterrupt")
            self.serviceExecutor.submit(self.serviceHandler.resumeAfterInterrupt)
        elif previousState == SUSPENDED:
            self.logger.debug("Executing resumeAfterSuspend")
            self.serviceExecutor.submit(self.serviceHandler.resumeAfterSuspend)
        else:
            self.logger.error("Unexpected previous state: {}".format(previousState))

        self.serviceExecutor.submit(self.releaseWaitLock)

    def goToSuspendedState(self):
        if not self.isConnected():
            self.logger.warning("Not going to SUSPENDED state while not connected")
            return
        self.state = SUSPENDED
        self.heartBeatMonitor.stop()

        self.serviceExecutor.submit(self.serviceHandler.onSuspend)

    def goToResumedState(self, newListenPort, newTargetAddress):
        if self.state != SUSPENDED:
            self.logger.warning("Unable to resume connection when not in SUSPENDED")
            return

        self.port = newListenPort
        self.targetAddress = newTargetAddress

        self.socket.close()
        self.socket = None

    def goToInterruptedState(self):
        if not self.isConnected():
            self.logger.warning("Not going to INTERRUPTED state while not connected")
            return

        self.state = INTERRUPTED
        if self.serviceHandler is not None:
            def futureFn():
                if self.state != TERMINATED:
                    self.serviceHandler.onInterrupt()
            self.serviceExecutor.submit(futureFn)

    def goToTerminatedState(self):
        self.close()

    def close(self):
        self.keepRunning = False
        with self.closeLock:

            if self.state != TERMINATED:
                self.state = TERMINATED
                if self.serviceHandler is not None:
                    self.serviceExecutor.submit(self.serviceHandler.terminated)

            if self.heartBeatMonitor is not None:
                self.heartBeatMonitor.stop()

            if self.socket is not None:
                self.socket.close()
                self.socket = None

            self.mqFuture.cancel()
            self.srFuture.cancel()

            self.connectionExecutor.shutdown(False)

    def socketReader(self):
        while self.keepRunning:
            if self.socket is not None:
                self.logger.debug("socketreader - Closing old socket")
                self.socket.close()

                if self.handShakeMonitor is not None:
                    self.handShakeMonitor.close()
                if self.heartBeatMonitor is not None:
                    self.heartBeatMonitor.close()

            self.logger.info("socketreader - Building TCPConnection {} {}".format(self.keepRunning, id(self)))
            if not self.targetAddress:
                self.socket = TCPSocket.asServer(self.port)
            else:
                self.socket = TCPSocket.asClient(self.targetAddress, self.port)

            try:
                self.socket.waitUntilConnected(1000)
            except Exception as e:
                if self.keepRunning:
                    self.logger.warning("socketreader - Interrupted while waiting for connection to establish ({})".format(e))
                    continue
                else:
                    break

            self.logger.debug("socketreader - Creating connection monitors")
            self.handShakeMonitor = HandShakeMonitor(self.socket, self.connectionId)
            self.heartBeatMonitor = HeartBeatMonitor(self.socket, self.connectionId)

            def futureFn():
                try:
                    self.logger.debug("socketreader - Initiating handshake")
                    self.handShakeMonitor.sendHandShake(self.getState())
                    self.handShakeMonitor.waitUntilFinished(0)
                    self.logger.debug("socketreader - Handshake confirmed, starting heartbeat")
                    self.heartBeatMonitor.start()
                    if self.handShakeMonitor is not None and not self.handShakeMonitor.closing:
                        self.goToConnectedState()
                except InterruptedError as e:
                    if self.keepRunning:
                        self.logger.warning("socketreader - Interrupted while waiting for TCP socket to initialize")

            self.connectionExecutor.submit(futureFn)

            while self.keepRunning:
                try:
                    data = self.socket.read()
                    if not data or data is None:
                        continue
                    else:
                        hbm = not self.heartBeatMonitor.handleMessage(data)
                        hsm = not self.handShakeMonitor.handleHandShake(data)
                        if hbm and hsm:
                            self.internalQueue.put(data)
                except IOError as e:
                    if self.keepRunning:
                        self.logger.warning("socketreader - IOError while reading from socket: {} (currentState: {})"
                                            .format(e, self.state))
                        self.goToInterruptedState()
                    else:
                        self.logger.debug("socketreader - IOError -> keepRunning false: {}".format(e))
                    break
                except OSError as e:
                    self.logger.warning('socketreader - OS exception when reading from socket: {}'.format(e))
                    break
                except Exception as e:
                    self.logger.warning('socketreader - Timeout exception: {}'.format(e))
                    break
            time.sleep(0.1)

    def messageQueue(self):
        while self.keepRunning:
            try:
                message = self.internalQueue.get(block=True, timeout=0.1)
                if not not message:
                    self.handleMessage(message)
            except Empty:
                continue
            except InterruptedError:
                self.logger.error("Message handler interrupted, stopping thread")
                break
