import socket
import abc
import time
import threading
import logging

from ..Exceptions import NotYetConnectedException


def currentTimeMillis():
    return int(round(time.time() * 1000))


class TCPSocket:
    _CONNECT_ON_SEND_TIMEOUT = 10
    _EOM = b'\xff'
    logger = None

    def __enter__(self): return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __init__(self, address, port):
        self.sock = None
        self.closed = False
        if address is not None:
            self.logger = logging.getLogger("defpi.TCPSocket (Client)")
            self.logger.debug("Creating TCPSocket Client")
            self.connector = ClientSocketConnector(address, port)
        else:
            self.logger = logging.getLogger("defpi.TCPSocket (Server)")
            self.logger.debug("Creating TCPSocket Server")
            self.connector = ServerSocketConnector(port)

    @staticmethod
    def asClient(host, port):
        return TCPSocket(host, port)

    @staticmethod
    def asServer(port):
        return TCPSocket(None, port)

    # def isConnected(self):
    #    return self.sock is not None  # self.sock.isConnected && self.sock.isClosed

    def waitUntilConnected(self, millis=None):
        if self.sock is not None:
            return True

        self.sock = self.connector.connect(millis)
        if self.sock is None:
            return False
        else:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            return True

    def recv(self, buffersize, timeout=0):
        self.sock.settimeout(0.1)
        t_start = currentTimeMillis()
        while not self.closed and (timeout == 0 or currentTimeMillis() - t_start < timeout):
            try:
                data = self.sock.recv(buffersize)
                return data
            except socket.timeout:
                self.logger.debug('Recv time out')
        self.logger.debug('Recv duration: {} timeout={} self.closed={}, '.format(currentTimeMillis()-t_start, timeout, self.closed))
        raise socket.timeout

    def read(self, timeout=0):
        try:
            t_start = currentTimeMillis()
            if timeout == 0:
                self.waitUntilConnected()
            else:
                if not self.waitUntilConnected(timeout):
                    self.logger.debug("Read timeout while waiting to connect")
                    time.sleep(0.1)
                    return None

            # Synchronised this.socket.getInputStream
            if timeout == 0:
                timeout2 = 0
            else:
                timeout2 = int((timeout - (currentTimeMillis() - t_start)))
                # self.sock.settimeout(max(0, timeout2))

            # msg_len_bytes = self.sock.recv(4)
            msg_len_bytes = self.recv(4, timeout2)
            msg_len = int.from_bytes(msg_len_bytes, byteorder='big')

            if msg_len < 0:
                self.logger.warning('Reached end of stream')
                raise IOError('Reached end of stream')
            if msg_len == 0:
                self.logger.warning('Received msg_len of 0')
                raise IOError('Reached end of stream')

            recv_bytes = b''
            while len(recv_bytes) < msg_len:
                # chunk = self.sock.recv(min(msg_len - len(recv_bytes), 2048))
                chunk = self.recv(min(msg_len - len(recv_bytes), 2048), timeout2)
                if chunk == '':
                    raise RuntimeError("socket connection broken")
                recv_bytes = recv_bytes + chunk

            if len(recv_bytes) != msg_len:
                self.logger.debug("Expected {} bytes, instead received {}", msg_len, len(recv_bytes))

            # eof = self.sock.recv(1)
            eof = self.recv(1, timeout2)
            if eof != self._EOM:
                self.logger.debug("Expected EOM, instead read {}, skipping stream".format(eof))
                while eof != self._EOM:
                    # eof = self.sock.recv(1)
                    eof = self.recv(1, timeout2)
                    if eof < 0:
                        self.logger.debug('Reached end of stream')
                        raise IOError("Reached end of stream")
            self.logger.debug("Read raw bytes: {}".format(recv_bytes))
            return recv_bytes
        except socket.timeout:
            self.logger.debug("Read timeout while waiting for data")
            return None
        except Exception as e:
            raise e

    def send(self, data):
        if not self.waitUntilConnected(self._CONNECT_ON_SEND_TIMEOUT):
            raise NotYetConnectedException("Not yet connected exception")
        if type(data) is not bytes:
            raise AttributeError("Data must be of bytes type")

        try:
            rawbytes = len(data).to_bytes(4, byteorder='big') + data + self._EOM
            result = self.sock.send(rawbytes)
            self.logger.debug("Sending raw bytes: {}".format(rawbytes))
            if result == 0:
                self.logger.debug("Sending failed")
        except BaseException as e:
            self.logger.debug("Sending failed exception ({})".format(str(e)))

    def close(self):
        self.logger.debug('Closing TCPSocket')
        self.closed = True
        self.connector.close()
        if self.sock is not None:
            self.sock.close()
        self.logger.debug('Successfully closed')


class SocketConnector:
    _INITIAL_BACKOFF_MS = 50
    _MAXMIMUM_BACKOFF_MS = 60000

    def __init__(self):
        self.backOff = self._INITIAL_BACKOFF_MS

    @abc.abstractmethod
    def connect(self, millis): raise NotImplementedError

    @abc.abstractmethod
    def close(self): raise NotImplementedError

    def increaseBackOffAndWait(self, max):
        self.backOff = min(max, min(self._MAXMIMUM_BACKOFF_MS, self.backOff * 1.25))
        time.sleep(self.backOff / 10000)

    def timeLeft(self, t_start, millis):
        return self._MAXMIMUM_BACKOFF_MS if millis == 0 or millis is None else max(0, millis - (currentTimeMillis() - t_start))


class ClientSocketConnector(SocketConnector):
    logger = logging.getLogger("defpi.ClientSocketConnector")

    def __init__(self, address, port):
        self.logger.debug("Creating Client Socket")
        self.targetAddress = address
        self.targetPort = port
        self.keepRunning = True
        super().__init__()

    def connect(self, millis):
        t_start = currentTimeMillis()
        while self.keepRunning and self.timeLeft(t_start, millis) > 0:
            self.logger.debug('Time left: {}'.format(self.timeLeft(t_start, millis)))
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.targetAddress, self.targetPort))
                self.logger.debug("Client connected: {}".format(sock))
                return sock
            except Exception as e:
                self.logger.debug("Unable to connect to {}:{}, retrying ({})".format(
                    self.targetAddress, self.targetPort, str(e)))
                self.increaseBackOffAndWait(self.timeLeft(t_start, millis))
                sock.close()


            time.sleep(0.1)
        return None

    def close(self):
        self.keepRunning = False


class ServerSocketConnector(SocketConnector):
    logger = logging.getLogger("defpi.ServerSocketConnector")

    def __init__(self, port):
        self.serverSocket = None
        self.logger.debug("Creating Server Socket")
        self.serverPort = port
        self.bindServerSocket()
        self.lock = threading.RLock()
        self.keepRunning = True
        super().__init__()

    def bindServerSocket(self):
        if self.serverSocket is not None:
            return True
        try:
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.serverSocket.bind(('0.0.0.0', self.serverPort))
            self.serverSocket.listen(5)
        except BaseException as e:
            self.logger.debug("Unable to open server socket at port {}, msg: {}".format(self.serverPort, str(e)))

    def connect(self, millis):
        t_start = currentTimeMillis()
        while self.keepRunning and self.serverSocket is None and (millis is None or self.timeLeft(t_start, millis) > 0):
            if not self.bindServerSocket():
                self.increaseBackOffAndWait(self.timeLeft(t_start, millis))

        if self.serverSocket is None:
            self.logger.debug("Server bind timed out")
            return None

        self.serverSocket.settimeout(millis)
        try:
            (client, address) = self.serverSocket.accept()
            self.serverSocket.close()
            self.logger.debug("Received client: {}".format(client))
            return client
        except socket.timeout:
            self.logger.debug("Server accept timed out")
            return None
        except OSError as e:
            self.logger.warning("Server socket accept OS error ({})".format(e))
            return None

    def close(self):
        self.keepRunning = False
