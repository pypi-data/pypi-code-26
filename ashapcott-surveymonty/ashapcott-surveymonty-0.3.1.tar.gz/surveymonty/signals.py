from blinker import Namespace

signals = Namespace()

response_received = signals.signal("response_received")
