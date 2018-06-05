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

    def __init__(self, font_color=(0, 0, 0)):
        self.canvas = screencanvas.ScreenCanvas(font_color=font_color)
        self.selection = ''
        self.centers = {}
        self.keyboard_hook = None
        self._font_color = font_color

    @property
    def font_color(self):
        return self._font_color

    @font_color.setter
    def font_color(self, value):
        self._font_color = value
        self.canvas.font_color = value
        self.canvas.render()

    def reset(self):
        self.canvas.reset()
        self.centers = {}
        self.selection = ''
        try:
            keyboard.unhook(self.keyboard_hook)
        except KeyError:
            pass

    def _on_key_press(self, click, key):
        if key.event_type == 'down':
            return
        if key.name in LETTERS:
            if len(self.selection) == 1:
                x, y = self.centers[f'{self.selection}{key.name}']
                mouse.move(x, y)
                if click:
                    mouse.click()
                self.empty()
            else:
                self.draw_letter_grid(row=key.name, click=click)
                self.selection += key.name
        elif key.name == 'backspace':
            self.draw_letter_grid(click=click)
        elif key.name == 'esc':
            self.empty()

    def draw_letter_grid(self, row=None, click=False):
        self.reset()
        self.keyboard_hook = keyboard.hook(functools.partial(self._on_key_press, click), suppress=True)
        letters = string.ascii_lowercase
        xsize, xremainder = divmod(self.canvas.width, len(letters))
        ysize, yremainder = divmod(self.canvas.height, len(letters))
        y = self.canvas.y
        for i, row_letter in enumerate(letters):
            x = self.canvas.x
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