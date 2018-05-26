#!/usr/bin/python3
# -*- coding: UTF-8 -*-


"""Modul contains statusbar implementation."""


__license__ = "Copyright 2018 by Vikarowitsch"
__author__ = "Vikarowitsch"


import tkinter as tk
from tkinter import StringVar
from tkinter import Label
from tkinter import FLAT
from statistic import Statistic

"""Moduls contains statusbar implementation."""


class GuiStatusbar(tk.Frame):

    """ Status Bar class - based on Frame."""

    def __init__(self, root):
        """Initialize an object."""
        tk.Frame.__init__(self, root)
        self.master = root

        self.time_used_in_secs = 0
        self.count_of_moves = 0
        self.count_of_move_buttons = 0
        self.current_moves = StringVar()
        self.current_moves.set(self.update_current_moves())
        self.moves_label = Label(self, relief=FLAT, textvariable=self.current_moves)
        self.moves_label.pack()
        self.pack(side=tk.BOTTOM, fill=tk.X)

    def update_current_moves(self):
        """Update the gui with statusbar values."""
        used_time = Statistic.format_duration(self.time_used_in_secs)
        self.current_moves.set(str("{0}Züge - {1}Knöpfe Spielzeit {2}".format(self.count_of_moves, self.count_of_move_buttons, used_time)))

    def set(self, moves, move_buttons, time_used_in_secs):
        """Set statusbar values."""
        self.count_of_moves = moves
        self.count_of_move_buttons = move_buttons
        self.time_used_in_secs = time_used_in_secs
        self.update_current_moves()
        self.moves_label.update_idletasks()

    def clear(self):
        """Initialize statusbar values."""
        self.count_of_moves = 0
        self.count_of_move_buttons = 0
        self.update_current_moves()
        self.moves_label.update_idletasks()
