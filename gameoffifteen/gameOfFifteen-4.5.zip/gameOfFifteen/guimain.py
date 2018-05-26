#!/usr/bin/python3
# -*- coding: UTF-8 -*-


"""Modul contains the main entry point to the gui."""


__license__ = "Copyright 2018 by Vikarowitsch"
__author__ = "Vikarowitsch"


import tkinter as tk
from guitoolbar import GuiToolbar
from gameframe import GameFrame
from guistatusbar import GuiStatusbar


class GuiMain(tk.Frame):

    """ main class for the application."""

    def __init__(self, root, *args, **kwargs):
        """Initialize an object."""
        super().__init__(root, *args, **kwargs)
        root.title('15er-Puzzle')
        root.geometry("340x400")
        self.center(root)
        self.guitoolbar = GuiToolbar(self)
        self.statusbar = GuiStatusbar(self)
        self.game_frame = GameFrame(self)
        self.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        root.configure(bg='black', padx=2, pady=2)
        root.resizable(0, 0)
        

    def center(self, toplevel):
        """Center the gui in the screen."""
        toplevel.update_idletasks()
        screen_width = toplevel.winfo_screenwidth()
        screen_height = toplevel.winfo_screenheight()
        size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
        x = screen_width/2 - size[0]/2
        y = screen_height/2 - size[1]/2
        toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

    def quit_application(self):
        quit()
    
