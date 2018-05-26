#!/usr/bin/python3
# -*- coding: UTF-8 -*-


"""Modul contains GuiToolbar implementation."""


__license__ = "Copyright 2018 by Vikarowitsch"
__author__ = "Vikarowitsch"

import os
from PIL import Image, ImageTk
from guistatistic import GuiStatistic
from statistic import Statistic
import tkinter as tk
from tkinter import Button
from tkinter import FLAT
import os

class GuiToolbar(tk.Frame):

    """Implement GuiToolbar."""

    def on_quit(self):
        """Implement the event quit application."""
        self.root.quit()

    def on_new_game(self):
        """Implement the event new game."""
        self.root.game_frame.on_new_game()

    def on_statistic(self):
        """Implement the event statistic gui."""
        dialog = GuiStatistic(self.root)
        self.root.wait_window(dialog)

    def __init__(self, root):
        """Construct object."""
        super().__init__(root)
        self.root = root
        
        maxsize = (32, 32)

        scriptPath = os.path.dirname(__file__)
        
        exit_png = Image.open("{0}/Icons/log-out-icon.png".format(scriptPath))
        exit_png.thumbnail(maxsize, Image.ANTIALIAS)
        exit_image = ImageTk.PhotoImage(exit_png)
        exit_button = Button(self, image=exit_image, relief=FLAT, command=self.on_quit)
        exit_button.image = exit_image
        exit_button.grid(row=0, column=1, sticky='w', padx=2, pady=2)

        new_png = Image.open("{0}/Icons/new-icon.png".format(scriptPath))
        new_png.thumbnail(maxsize, Image.ANTIALIAS)
        new_image = ImageTk.PhotoImage(new_png)
        new_button = Button(self, image=new_image, relief=FLAT, command=self.on_new_game)
        new_button.image = new_image
        new_button.grid(row=0, column=2, sticky='w', padx=2, pady=2)

        statistic_png = Image.open("{0}\Icons\chart-icon.png".format(scriptPath))
        statistic_png.thumbnail(maxsize, Image.ANTIALIAS)
        statistic_image = ImageTk.PhotoImage(statistic_png)
        statistic_button = Button(self, image=statistic_image, relief=FLAT, command=self.on_statistic)
        statistic_button.image = statistic_image
        statistic_button.grid(row=0, column=3, sticky='w', padx=2, pady=2)

        self.pack(side=tk.TOP, fill=tk.X)
