from .device import Device


class Navio2Device(Device):
    def __init__(self):
        super(Navio2Device, self).__init__("/etc/emlid/tests/navio2.json")
