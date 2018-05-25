from .devices.navio2device import Navio2Device
from .devices.naviodevice import NavioDevice
from .devices.edgedevice import EdgeDevice
from .devices.nodevice import NoDevice


class DeviceFactory:
    def __init__(self, info):
        self.info = info

    def create(self):
        if self.info.product == 'Navio 2':
            device = Navio2Device()
        elif self.info.product == 'Navio+':
            device = NavioDevice()
        elif self.info.product == 'Edge':
            device = EdgeDevice()
        else:
            device = NoDevice()
            return device

        return device
