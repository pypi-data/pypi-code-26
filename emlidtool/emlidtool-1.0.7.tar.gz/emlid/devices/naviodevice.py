from .device import Device


class NavioDevice(Device):
    def __init__(self):
        super(NavioDevice, self).__init__("/etc/emlid/tests/navio.json")
