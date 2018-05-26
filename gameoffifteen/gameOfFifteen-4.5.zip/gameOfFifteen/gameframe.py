#!/usr/bin/python3
# -*- coding: UTF-8 -*-


"""Modul contains game frame of the gui."""


__license__ = "Copyright 2018 by Vikarowitsch"
__author__ = "Vikarowitsch"


import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import font
from tkinter import Grid
from tkinter import X,  BOTTOM
from game import Game
from statistic import Statistic


class GameFrame(tk.Frame):

    """The sort buttons gui and functions."""

    red_numbers = [1, 3, 6, 8, 9, 11, 14]
    white_numbers = [2, 4, 5, 7, 10, 12, 13, 15]

    def __init__(self, root, *args, **kwargs):
        """Constructor."""
        super().__init__(root, *args, **kwargs)
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        self.game = Game()
        self.statistic = Statistic()
        self.init_gui()
        self.pack(side=BOTTOM, fill=X)

    def init_gui(self):
        """Build GUI."""
        for column_index in range(0, self.game.column_count):
            Grid.columnconfigure(self, column_index, weight=1)
        for row_index in range(0, self.game.row_count):
            Grid.rowconfigure(self, row_index, weight=1)
        self.configure(bg='black', padx=2, pady=2)
        self.prepare_new_game()

    def on_enter(self, event):
        """Handle button mouse enter event."""
        move_count = self.root.statusbar.count_of_moves
        move_count_button = self.root.statusbar.count_of_move_buttons
        button = event.widget
        button_number = int(button["text"])
        if self.game.is_move_possible(button_number):
            move_count = move_count + 1
            selected_row = self.game.row_of_value(button_number)
            selected_column = self.game.column_of_value(button_number)
            hole_row = self.game.row_of_value(0)
            hole_column = self.game.column_of_value(0)

            if selected_row == hole_row:
                # move horizontal
                if selected_column < hole_column:
                    # move all to the right
                    while selected_column < hole_column:
                        move_count_button = move_count_button + 1
                        button = self.find_in_grid(self, hole_column - 1, hole_row)
                        button.grid(column=hole_column, row=hole_row)
                        self.game.move_to_hole(hole_column - 1, hole_row)
                        hole_column = hole_column - 1
                else:
                    # move all to left
                    while selected_column > hole_column:
                        move_count_button = move_count_button + 1
                        button = self.find_in_grid(self, hole_column + 1, hole_row)
                        button.grid(column=hole_column, row=hole_row)
                        self.game.move_to_hole(hole_column + 1, hole_row)
                        hole_column = hole_column + 1
            else:
                # move vertical
                if selected_row < hole_row:
                    # move all up
                    while selected_row < hole_row:
                        move_count_button = move_count_button + 1
                        button = self.find_in_grid(self, hole_column, hole_row - 1)
                        button.grid(column=hole_column, row=hole_row)
                        self.game.move_to_hole(hole_column, hole_row - 1)
                        hole_row = hole_row - 1
                else:
                    # move all down
                    while selected_row > hole_row:
                        move_count_button = move_count_button + 1
                        button = self.find_in_grid(self, hole_column, hole_row + 1)
                        button.grid(column=hole_column, row=hole_row)
                        self.game.move_to_hole(hole_column, hole_row + 1)
                        hole_row = hole_row + 1

            used_game_time = int((datetime.datetime.now() - self.startGameTime).total_seconds())
            self.root.statusbar.set(move_count, move_count_button, used_game_time)
            solution_name = self.game.all_sorted()
            if solution_name is not None:
                self.statistic.add(solution_name, move_count, move_count_button, used_game_time)
                messagebox_return = messagebox.askretrycancel(solution_name, "Play again", )
                if messagebox_return is False:
                    self.on_quit()
                else:
                    self.prepare_new_game()

    def prepare_new_game(self):
        """Setup a new game."""
        self.startGameTime = datetime.datetime.now()
        self.root.statusbar.clear()
        button_font = font.Font(family='Helvetica', size=32, weight='bold')
        self.game.shuffle()
        for column_index in range(0, self.game.column_count):
            for row_index in range(0, self.game.row_count):
                button = self.find_in_grid(self, column_index, row_index)
                if button is not None:
                    button.destroy()
                if self.game.value_at(column_index, row_index) == 0:
                    continue
                else:
                    number = self.game.value_at(column_index, row_index)
                    background = self.get_background_of(number)
                    foreground = 'gold'
                    button = tk.Button(self, width=3, height=1, fg=foreground, bg=background, font=button_font, text=repr(self.game.value_at(column_index, row_index)).rjust(2))
                    button.bind("<Enter>", self.on_enter)
                    button.grid(column=column_index, row=row_index)

    def get_background_of(self, number):
        """Return the background color for this number as string."""
        if number in GameFrame.red_numbers:
            return 'red'
        if number in GameFrame.white_numbers:
            return 'white'
        return 'lightgrey'

    def on_new_game(self):
        """Prepare a new game."""
        self.prepare_new_game()

    def on_quit(self):
        """Exit program."""
        self.root.quit()

    def find_in_grid(self, frame, column, row):
        """Find a widget in the grid and returns it."""
        for child in frame.children.values():
            info = child.grid_info()
            try:
                if info['row'] == row and info['column'] == column:
                    return child
            except:
                pass
        return None
