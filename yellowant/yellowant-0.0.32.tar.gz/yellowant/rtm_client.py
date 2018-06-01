from socketIO_client import SocketIO as SocketIOClient


class RTMEvents(object):
    """All socket events recognized by this server
    """
    CONNECT = "connect" # connection
    DISCONNECT = "disconnect" # disconnection from client
    ERROR = "error" # client errors
    YELLOWANT_COMMAND = "yellowant_command" # YellowAnt command from server
    YELLOWANT_MESSAGE = "yellowant_message" # YellowAnt message from client
    YELLOWANT_WEBHOOK_SUBSCRIPTION = "yellowant_webhook_subscription" #  YellowAnt webhook subscription from server


class RTMClient(object):
    def __init__(self, rtm_token, client_id, host="https://rtm.yellowant.com/", port=80):
        self.client = SocketIOClient(host, port, params={"rtm_token": rtm_token, "client_id": client_id})
    
    def wait(self):
        self.client.wait()
    
    def disconnect(self):
        self.client.disconnect()
    
    def bind_connect_event_handler(self, on_connect):
        self.client.on(RTMEvents.CONNECT, on_connect)
    
    def bind_disconnect_event_handler(self, on_disconnect):
        self.client.on(RTMEvents.DISCONNECT, on_disconnect)
    
    def bind_yellowant_command_event_handler(self, on_yellowant_command):
        def data_handler(data):
            return on_yellowant_command(data.get("event_id"), data.get("request_data"))
        self.client.on(RTMEvents.YELLOWANT_COMMAND, data_handler)
    
    def bind_yellowant_webhook_subscription_event_handler(self, on_yellowant_webhook_subscription):
        self.client.on(RTMEvents.YELLOWANT_WEBHOOK_SUBSCRIPTION, on_yellowant_webhook_subscription)
    
    def bind_error_event_handler(self, on_error):
        self.client.on(RTMEvents.ERROR, on_error)
    
    def emit_yellowant_message(self, event_id, yellowant_message):
        data = {
            "event_id": event_id,
            "message": yellowant_message,
        }
        self.client.emit(RTMEvents.YELLOWANT_MESSAGE, data)