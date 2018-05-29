from __future__ import unicode_literals

import socket
import time
import select
import json

from rasahub import RasahubPlugin

class RasaConnector(RasahubPlugin):
    """
    RasaConnector is subclass of RasahubPlugin to connect to Rasa Cores
    RasahubInputChannel
    """

    def __init__(self,
                 host = '127.0.0.1',
                 port = 5020):
        """
        Initializes the RasaConnector, establishes the server socket

        :param host: IP address of Rasa_Core instance
        :type name: str.
        :param port: Port number set in Rasa_Core RasahubInputChannel
        :type state: int.
        """
        super(RasaConnector, self).__init__()

        rasasocket = socket.socket()
        rasasocket.bind((host, port))
        rasasocket.listen(5)
        c, addr = rasasocket.accept()
        self.con = c

    def send(self, messagedata, main_queue):
        """
        Sends message to Rasa via socket connection
        messagedata is RasahubMessage object
        """
        sending = {
            'message': messagedata.message,
            'message_id': messagedata.message_id
        }
        self.con.send(json.dumps(sending).encode())

    def receive(self):
        """
        Receives message from socket connection to Rasa

        :param messagedata: Input message as string and conversation ID
        :type name: dictionary.
        :returns: dictionary - the reply from Rasa as string and conversation ID as string
        """
        timeout = time.time() + 5
        ready = select.select([self.con], [], [], 5)
        if ready[0]:
            reply = self.con.recv(1024).decode('utf-8')
            reply = json.loads(reply)
            replydata = {
                'message': reply['message'],
                'message_id': reply['message_id']
            }
            return replydata
        else:
            return None

    def end(self):
        """
        Shuts down socket connection
        """
        self.con.shutdown(socket.SHUT_RDWR)
