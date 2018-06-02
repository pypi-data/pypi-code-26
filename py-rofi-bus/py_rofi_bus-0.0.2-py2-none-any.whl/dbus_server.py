#!/usr/bin/env python3
#!

# pylint:disable=W,C,R

from pydbus import SessionBus
from gi.repository import GLib
import random

from xpybutil.ewmh import (
    get_client_list,
    get_wm_desktop,
    request_active_window,
    request_current_desktop,
)

INTERFACE_NAME = "pro.wizardsoftheweb.pyrofibus"


def global_window_id_list():
    return get_client_list().reply()


class RofiDbus(object):
    dbus = """
    <node>
        <interface name='{}'>
            <method name='UpdateActiveWindow'>
                <arg type='i' name='a' direction='in'/>
            </method>
            <method name='ActivateWindow'>
                <arg type='i' name='a' direction='in'/>
            </method>
            <method name='GetWindowList'>
                <arg type='ai' name='response' direction='out'/>
            </method>
        </interface>
    </node>
    """.format(INTERFACE_NAME)
    window_ids = global_window_id_list()

    def UpdateActiveWindow(self, active_window_id):
        global_window_ids = global_window_id_list()
        if active_window_id in self.window_ids:
            self.window_ids.remove(active_window_id)
        self.window_ids.insert(0, active_window_id)
        current_window_ids = self.window_ids[:]
        for window_id in global_window_ids:
            if window_id in self.window_ids:
                current_window_ids.remove(window_id)
            else:
                self.window_ids.append(window_id)
        for window_id in current_window_ids:
            self.window_ids.remove(window_id)

    def ActivateWindow(self, window_id):
        request_current_desktop(get_wm_desktop(window_id).reply())
        request_active_window(window_id)

    def GetWindowList(self):
        return self.window_ids


def cli():
    loop = GLib.MainLoop()
    bus = SessionBus()
    bus.publish(INTERFACE_NAME, RofiDbus())
    try:
        loop.run()
    except KeyboardInterrupt:
        loop.quit()

if '__main__' == __name__:
    cli()
