# pylint:disable=W,C,R
from pydbus import SessionBus
from pydbus.bus import Bus
from gi.repository.GLib import MainLoop


class Daemon(object):
    INTERFACE_NAME = "pro.wizardsoftheweb.pyrofibus.daemon"
    dbus = """
    <node>
        <interface name='{}'>
            <method name='is_running'>
                <arg type='b' name='response' direction='out'/>
            </method>
            <method name='start'>
            </method>
            <method name='stop'>
            </method>
        </interface>
    </node>
    """.format(INTERFACE_NAME)

    _is_running = False

    def __init__(self, bus=None, loop=None):
        if bus is None:
            self.bus = SessionBus()
        else:
            self.bus = bus
        if loop is None:
            self.loop = MainLoop()
        else:
            self.loop = loop

        self.bus.publish(self.INTERFACE_NAME, self)

    def start(self):
        if not self._is_running:
            try:
                self._is_running = True
                self.loop.run()
            except KeyboardInterrupt:
                self.loop.quit()
                self._is_running = False

    def is_running(self):
        return self._is_running

    def stop(self):
        self.loop.quit()
        self._is_running = False

    @staticmethod
    def bootstrap():
        daemon = Daemon()
        daemon.start()

if '__main__' == __name__:
    Daemon.bootstrap()
