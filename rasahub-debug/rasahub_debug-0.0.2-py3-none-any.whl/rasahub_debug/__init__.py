from rasahub import RasahubPlugin

import json
import sys
import socket
import time
import select

is_py2 = sys.version[0] == '2'

class DebugConnector(RasahubPlugin):
    """
    Debugging Connector for Rasahub
    """

    def __init__(self, host = '127.0.0.1', port = 5020):
        super(DebugConnector, self).__init__()

        self.ip = host
        self.port = port

        try:
            rasasocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            rasasocket = None
            print("socket could not be established")
            print(msg)
            raise Exception(msg)
        try:
            rasasocket.bind((self.ip, self.port))
            rasasocket.listen(5)
        except socket.error as msg:
            rasasocket.close()
            rasasocket = None
            print("port could not be opened")
            print(msg)
            raise Exception(msg)

        c, addr = rasasocket.accept()
        self.con = c

    def send(self, messagedata, main_queue):
        """
        sends to console log
        """
        sending = {
            'message': messagedata.message,
            'message_id': messagedata.message_id
        }
        self.con.send(json.dumps(sending).encode())

    def receive(self):
        """
        receives message from keyboard input
        """
        timeout = time.time() + 5
        ready = select.select([self.con], [], [], 5)
        if ready[0]:
            reply = self.con.recv(1024).decode('utf-8')
            print(reply)
            if len(reply) > 0 and reply is not None:
                print("raw " + reply)
                try:
                    reply = json.loads(reply)
                    replydata = {
                        'message': reply['message'],
                        'message_id': reply['message_id']
                    }
                    print(replydata)
                    return replydata
                except:
                    pass
        else:
            return None

    def process_command(self, command, payload):
        """
        Debug command hook
        """
        print(command)
        print(payload)
        return_message = {
            'message': {
                'reply': 'processed command',
                'message_id': payload['message_id']
            },
            'source': self.target,
            'target': self.name
        }
        return return_message

    def end(self):
        """
        Shuts down socket connection to debug client
        """
        self.con.shutdown(socket.SHUT_RDWR)
