import string
import keyboard
from screengrid import screencanvas

import win32api, win32con, win32gui, win32ui
import threading
import time
import string
import ctypes
import functools
import mouse

LETTERS = set(string.ascii_lowercase)

class Grid:

    def __init__(self):
        self.canvas = screencanvas.ScreenCanvas()
        self.selection = ''
        self.centers = {}
        self.keyboard_hook = None

    def reset(self):
        self.canvas.reset()
        self.centers = {}
        try:
            keyboard.unhook(self.keyboard_hook)
        except KeyError:
            pass

    def _on_key_press(self, key):
        if key.event_type == 'down':
            return
        if key.name in LETTERS:
            if len(self.selection) == 1:
                x, y = self.centers[f'{self.selection}{key.name}']
                mouse.move(x, y)
                self.empty()
            else:
                self.draw_letter_grid(row=key.name)
                self.selection += key.name
        elif key.name == 'backspace':
            self.draw_letter_grid()
        elif key.name == 'esc':
            self.empty()

    def draw_letter_grid(self, row=None):
        self.reset()
        self.keyboard_hook = keyboard.hook(self._on_key_press, suppress=True)
        letters = string.ascii_lowercase
        xsize = self.canvas.width // len(letters)
        xremainder = self.canvas.width % len(letters) 
        ysize = self.canvas.height // len(letters)
        yremainder = self.canvas.height % len(letters)
        y = 0
        for i, row_letter in enumerate(letters):
            x = 0
            recheight = ysize
            if i < yremainder:
                recheight += 1
            if row is None or row == row_letter:
                for j, col_letter in enumerate(letters):
                    recwidth = xsize
                    if j < xremainder:
                        recwidth += 1
                    self.centers[f'{row_letter}{col_letter}'] = x + recwidth//2, y + recheight//2
                    self.canvas.add_rectangle(x, y, recwidth, recheight, f'{row_letter}{col_letter}')
                    x += recwidth
            y += recheight
        self.canvas.render()

    def empty(self):
        self.reset()
        self.canvas.render()