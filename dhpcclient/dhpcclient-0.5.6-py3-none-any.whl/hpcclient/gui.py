
import os
import sys

dirname = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, dirname)

import threading
import wx
import wx.adv
import hpcclient

TRAY_ICON = dirname+'/testicon.png'


def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class SysTray(wx.adv.TaskBarIcon):
    def __init__(self, frame, app, client):
        self.frame = frame
        self.app = app
        self.client = client
        super(SysTray, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Deactivate', self.pause_running_tasks)
        create_menu_item(menu, 'Activate', self.start_paused_tasks)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.exit)
        return menu

    def set_icon(self, path):
        icon = wx.Icon(wx.Bitmap(path))
        self.SetIcon(icon, 'HPCClient')

    def pause_running_tasks(self, evt):
        self.client.deactivate()

    def start_paused_tasks(self, evt):
        self.client.activate()

    def exit(self, evt):
        self.Unbind(wx.adv.EVT_TASKBAR_LEFT_DOWN)
        self.app.ExitMainLoop()

    def left_down(self, evt):
        pass

class GUI(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(GUI, self).__init__(*args, **kwargs)
        self.init()

    def init(self):
        self.SetSize((0, 0))
        self.Show(False)

def main():
    app = wx.App()
    gui = GUI(None)
    client = hpcclient.HPCClient(daemonize=False)
    t = threading.Thread(target=client.run, name='hpcclient_client.run')
    t.start()

    SysTray(gui, app, client)

    app.MainLoop()

if(__name__ == '__main__'):
    main()

