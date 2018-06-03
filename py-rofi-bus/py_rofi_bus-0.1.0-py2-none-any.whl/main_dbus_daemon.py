# pylint:disable=W,C,R
from py_rofi_bus.components import Daemon as DaemonProcess
from py_rofi_bus.dbus import Daemon as DaemonServer


class MainDbusDaemon(DaemonProcess):

    def main(self):
        DaemonServer.bootstrap()

if '__main__' == __name__:
    MainDbusDaemon.bootstrap()
