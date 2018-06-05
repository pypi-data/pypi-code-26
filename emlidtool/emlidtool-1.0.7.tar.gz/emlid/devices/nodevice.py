from .device import Device


class NoDevice(Device):
    def __init__(self):
        super(NoDevice, self).__init__("/etc/emlid/tests/nodevice.json")
