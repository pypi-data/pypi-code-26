import websocket
import json
import base64
import hmac
import hashlib
import pkg_resources

class SocketManager():
    def __init__(self, on_message_callback, ip, secret_key, public_key, channel_name, params, global_identifier):

        self.ws = websocket.WebSocketApp(
            "ws://%s/cable" %(ip),
            on_message=self._on_message,
            on_error=self._on_error,
        )
        self.ws.on_open = self._on_open
        self.on_message_callback = on_message_callback
        self.ip = ip
        self.secret_key = secret_key
        self.public_key = public_key
        self.channel_name = channel_name
        self.global_identifier = global_identifier
        self.params = params
        self.retry_connection = True

        globals()[global_identifier] = self


    def stop(self):
        self.websocket_status = 'DISCONNECTED - NOT RETRYING'
        self.ws.keep_running = False
        self.retry_connection = False
        self.ws.close()


#  __________________________ PRIVATE METHODS ___________________________________________

    def _on_message(self, ws, message):
        self.websocket_status = 'CONNECTED'
        self.on_message_callback(message)

    def _on_error(self, ws, error):
        self.websocket_status = 'DISCONNECTED - RETRYING'
        self.websocket_connected = False

    def _on_open(self, ws):
        def run(*args):
            ws.send(json.dumps({
                "command": "subscribe",
                "identifier": json.dumps({
                    "channel": self.channel_name,
                    "client_version": pkg_resources.get_distribution("livedataframe").version,
                    **self.params,
                    "public_key": self.public_key,
                    "signature": self._create_signature(self.secret_key, self.channel_name).decode('ascii'),
                })
            }))

        run()

    def _create_signature(self, secret, message):
        message = bytes(message, 'utf-8')
        secret = bytes(secret, 'utf-8')
        hash = hmac.new(secret, message , hashlib.sha256)

        return base64.b64encode(hash.digest())

    def _run_forever_patch(self):
        while self.retry_connection:
            try:
                self.ws.run_forever()
            except Exception as e:
                pass
