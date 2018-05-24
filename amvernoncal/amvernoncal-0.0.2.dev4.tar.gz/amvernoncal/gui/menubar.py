import datetime
import gettext
import sys
import time
import tkinter
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename
from dialogs import PopupDialog

class MenuBar(tkinter.Menu):
    """
        MenuBar with "File" and "Help" drop-downs
    """

    def __init__(self, parent):
        tkinter.Menu.__init__(self, parent)

        # File Menu
        filemenu = tkinter.Menu(self, tearoff=False)
        filemenu.add_command(label='Exit',
                             underline=1,
                             command=self.quit)

        # Help Menu
        helpmenu = tkinter.Menu(self, tearoff=False)
        helpmenu.add_command(label='Help',
                             command=lambda x=None: self.help_dialog('Help.'),
                             accelerator="F1")
        helpmenu.add_command(label='About', command=self.about_dialog)
        self.bind_all('<F1>', self.help_dialog)

        self.add_cascade(label='File', underline=0, menu=filemenu)
        self.add_cascade(label='Help', underline=0, menu=helpmenu)

    def quit(self):
        sys.exit(0)

    def help_dialog(self, event):
        _description = """
            Help section not created yet.  Wah wah wah...
        """
        PopupDialog(self, 'Arthur Murray Vernon Calendar', _description)

    def about_dialog(self):
        _description = """
            A Tkinter GUI for amvernoncal

            Author: Vincent Chov
            Email: vincent.chov@uconn.edu
            Version: 0.0.1
            GitHub Package : amvernoncal
        """
        PopupDialog(self, 'About', _description)


