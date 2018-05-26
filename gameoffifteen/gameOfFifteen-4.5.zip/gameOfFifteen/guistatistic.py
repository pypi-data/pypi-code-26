#!/usr/bin/python3
# -*- coding: UTF-8 -*-


"""Modul contains scripts for setup."""


__license__ = "Copyright 2018 by Vikarowitsch"
__author__ = "Vikarowitsch"


from tkinter import *
from statistic import Statistic

class GuiStatistic(Toplevel):

    """Implement the GUI for statistic."""

    def __init__(self, parent):
        """Implement the object creation."""
        top = self.top = Toplevel.__init__(self, parent)
        self.transient(parent)
        self.parent = parent
        self.body = Frame(self)
        self.initial_focus = self.body
        self.winfo_toplevel().title("Statistik")

        Grid.columnconfigure(self, 0, weight=1, minsize=500)
        Grid.rowconfigure(self, 0, weight=1, minsize=300)
       
        self.listbox = Listbox(self)
        self.scrollbar = Scrollbar(self.listbox, orient=VERTICAL)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        for item in Statistic.get_statistic():
            self.listbox.insert(END, item)

        ok_button = Button(self, text="OK", width=10, command=self.ok)

        self.listbox.grid(column=0, row=0, columnspan=2, sticky=N+E+W+S)
        self.listbox.columnconfigure(0, weight=1)        
        self.listbox.rowconfigure(0, weight=1)        
        self.scrollbar.grid(column=1, row=0, sticky=N+S+E)

        ok_button.grid(column=0, row=1)
        self.resizable(0, 0)
        self.center(self)

    def center(self, toplevel):
        """Implement the GUI in the center of the screen."""
        toplevel.update_idletasks()
        screen_width = toplevel.winfo_screenwidth()
        screen_height = toplevel.winfo_screenheight()
        size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
        x = screen_width/2 - size[0]/2
        y = screen_height/2 - size[1]/2
        toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

    def ok(self):
        """Implement the ovent ok."""
        self.destroy()
