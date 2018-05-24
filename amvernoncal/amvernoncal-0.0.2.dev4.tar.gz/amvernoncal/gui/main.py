import datetime
import gettext
import sys
import time
import tkinter
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename
from dialogs import PopupDialog
from toolbar import ToolBar
from menubar import MenuBar


class MainFrame(ttk.Frame):
    """
        It will take a while to get into the mainframe.
    """

    past_time = datetime.datetime.now()
    _product = 'Arthur Murray Vernon Calendar\n\n'

    def __init__(self, parent):
        """
            We're in!
        """
        ttk.Frame.__init__(self, parent)
        self.display = ttk.Label(parent, anchor=tkinter.CENTER,
                                 foreground='green', background='black')
        self.display.pack(fill=tkinter.BOTH, expand=1)
        self.tick()

    def tick(self):
        """
            Automatically updates a clock
        """

        this_time = datetime.datetime.now()
        if this_time != self.past_time:
            self.past_time = this_time
            _timestamp = this_time.strftime('%Y-%m-%d %H:%M:%S')
            self.display.config(text=self._product + _timestamp)
        self.display.after(100, self.tick)


class Application(tkinter.Tk):
    """
        Top-level Tkinter widget.
    """

    def __init__(self):
        tkinter.Tk.__init__(self)
        menubar = MenuBar(self)
        self.config(menu=menubar)
        self.wm_title('Arthur Murray Vernon Calendar')
        self.wm_geometry('640x480')

        # Tool bar selection == 'y'
        self.toolbar = ToolBar(self)
        self.toolbar.pack(side='top', fill='x')

        self.mainframe = MainFrame(self)
        self.mainframe.pack(side='right', fill='y')


if __name__ == '__main__':
    APPLICATION_GUI = Application()
    APPLICATION_GUI.mainloop()
