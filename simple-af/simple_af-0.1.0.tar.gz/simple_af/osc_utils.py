from OSC import ThreadingOSCServer
from OSC import OSCClient
from OSC import OSCMessage
from OSC import OSCBundle
from threading import Thread
from collections import namedtuple, defaultdict
import atexit

defaults = {'address': '0.0.0.0', 'port': 7000}
button_path = "/button"
BUTTON_OFF = 0
BUTTON_ON = 1
BUTTON_TOGGLE = 2


class OSCStorage(object):
    def __init__(self):
        self.accumulating = {'midi':[]}
        self.current = {}
        self.last = {}

    def next_frame(self):
        #TODO: This is an ugly way to initialize. We should be using a default dict and a queue
        self.last, self.current, self.accumulating = self.current, self.accumulating, {'midi':[]}

def create_osc_server(host=defaults['address'], port=defaults['port']):
    # String, int -> OSCServer

    server = ThreadingOSCServer((host, port))
    thread = Thread(target=server.serve_forever)
    thread.setDaemon(True)
    thread.start()

    # TODO: atexit.register(self.disconnect())
    return server


def get_osc_client(host='localhost', port=defaults['port']):
    # String, int -> OSCClient

    client = OSCClient()
    client.connect((host, port))

    return client


def send_simple_message(client, path, data=[], timeout=None):
    # OSCClient, String, String, int -> None
    msg = OSCMessage(path)
    for d in data:
        msg.append(d)
    client.send(msg, timeout)