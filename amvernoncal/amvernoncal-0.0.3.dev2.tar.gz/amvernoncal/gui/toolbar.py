import datetime
import gettext
import sys
import time
import tkinter
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename


class ToolBar(ttk.Frame):
    """
        ToolBar that sits below the MenuBar.
    """
    def __init__(self, parent):
        """
            Provides the option for gcal_to_xlsx or pdf_to_json
        """
        ttk.Frame.__init__(self, parent)

        # Tool 1: gcal_to_xlsx
        gcal_tool = ttk.Button(self,
                               text="Google Calendar to Excel",
                               command=self.gcal_to_xlsx)

        # Tool 2: pdf_to_json
        pdf_tool = ttk.Button(self,
                              text="PDF to JSON",
                              command=self.pdf_to_json)

        self.buttons = [x.pack(side=tkinter.LEFT, fill=tkinter.X)
                        for x in [gcal_tool, pdf_tool]]

        self.config(border=1, relief=tkinter.GROOVE)
        self.pack()

    def gcal_to_xlsx(i):
        name = tkinter.filedialog.askopenfilename()
        if isinstance(name, str):
            print('File selected for open: ' + name)
        else:
            print('No file selected')

    def pdf_to_json(i):
        name = tkinter.filedialog.askopenfilename()
        if isinstance(name, str):
            print('File selected for open: ' + name)
        else:
            print('No file selected')
