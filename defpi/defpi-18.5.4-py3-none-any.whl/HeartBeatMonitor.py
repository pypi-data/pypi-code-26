import logging

from defpi.common.ScheduledExecutor import ScheduledExecutor


class HeartBeatMonitor:
    logger = logging.getLogger("defpi.HeartBeatMonitor")

    _HEARTBEAT_PERIOD_IN_SECONDS = 10
    _HEARTBEAT_INITIAL_DELAY = 1

    _PING = b'\x0A'
    _PONG = b'\x0B'

    _MAX_MISSED_HEARTBEATS = 2

    threadCount = 0

    def __init__(self, socket, connectionId):
        self.socket = socket
        self.connectionId = connectionId
        self.executor = None

        self.heartBeatFuture = None
        self.receivedPong = None
        self.missedHeartBeats = 0

    def handleMessage(self, data):
        if len(data) != len(self._PING):
            return False

        if data == self._PONG:
            self.receivedPong = True
            self.missedHeartBeats = 0
            return True
        elif data == self._PING:
            try:
                self.socket.send(self._PONG)
            except Exception:
                self.logger.warning("[{}] - Unable to reply heartbeat, closing socket".format(self.connectionId))
                self.socket.close()
            return True

        return False

    def start(self):
        if self.executor is not None:
            self.executor.stop()

        self.executor = ScheduledExecutor(self._HEARTBEAT_PERIOD_IN_SECONDS,
                                          self._HEARTBEAT_INITIAL_DELAY,
                                          self.schedulePingPong)
        self.receivedPong = True
        self.missedHeartBeats = 0

    def close(self):
        self.stop()
        self.socket.close()

    def stop(self):
        if self.executor is not None:
            self.executor.stop()
            self.executor = None

    def schedulePingPong(self):
        try:
            if not self.receivedPong:
                self.logger.warning("[{}] - Missed a heartbeat,,".format(self.connectionId))
                self.missedHeartBeats += 1
                if self.missedHeartBeats > self._MAX_MISSED_HEARTBEATS:
                    self.logger.warning("[{}] - Missed more than {} heartbeats, closing socket".format(
                        self.connectionId, self._MAX_MISSED_HEARTBEATS))
                    self.close()

            try:
                self.receivedPong = False
                self.socket.send(self._PING)
            except Exception as e:
                self.logger.warning("[{}] - Unable to send heartbeat, closing socket: {}".format(self.connectionId, e))
                self.close()
        except Exception as e:
            self.logger.error("[{}] - Error while sending heartbeat: {}".format(self.connectionId, e))

