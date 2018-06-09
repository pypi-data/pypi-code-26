import hashlib
import hmac
import time
import json
import websocket
from .cipher import Cipher
from .request import Request
try:
    import thread
except ImportError:
    import _thread as thread
import time

class WebsocketClient():
    ENDPOINT = 'wss://ws.coinfalcon.com'

    def __init__(self, key, secret, endpoint = ENDPOINT):
        self.endpoint = endpoint
        self.channels = []
        self.cipher = Cipher(key, secret)

    def on_message(self, ws, message):
        print(message)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws):
        for channel in self.channels:
            ws.send(json.dumps(channel))

    def sign(self):
        request = Request('GET', '/auth/feed', None)
        self.cipher.sign(request)

        return request.headers

    def feed(self):
        ws = websocket.WebSocketApp("wss://ws.coinfalcon.com",
                                  on_message = self.on_message,
                                  on_error = self.on_error,
                                  on_close = self.on_close,
                                  header = self.sign())
        ws.on_open = self.on_open
        ws.run_forever()
