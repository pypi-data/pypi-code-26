from .device import Device


class EdgeDevice(Device):
    def __init__(self):
        super(EdgeDevice, self).__init__("/etc/emlid/tests/edge.json")
