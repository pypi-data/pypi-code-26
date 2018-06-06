"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from tornado import gen
from tornado.iostream import IOStream, StreamClosedError
import socket
import os


class LocalBrewPatron(object):
    def __init__(self, sock, brew, patron_id, brewer_id, callback):
        self.brew = brew
        self.patron_id = patron_id
        self.brewer_id = brewer_id
        self.callback = callback

        self.running = True

        if os.name == 'nt' or brew._settings['use_localhost'] \
                or type(sock) is list:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock = (sock[0], sock[1])
        else:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        self.stream = IOStream(self.socket)
        self.stream.connect(sock, callback=self._read_data)

    def stop(self):
        self.running = False
        self.stream.close()

    @gen.coroutine
    def _read_data(self):  # pragma no cover
        while self.running:
            try:
                data = yield self.stream.read_until(
                    self.brew._settings['delimiter'])
                data = data[:-4]
                self.callback(self.brewer_id, data)
            except StreamClosedError:
                self.stop()
