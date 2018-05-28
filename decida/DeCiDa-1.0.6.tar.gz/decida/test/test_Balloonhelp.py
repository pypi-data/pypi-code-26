#! /usr/bin/env python
from decida.Balloonhelp import Balloonhelp
from Tkinter import *
tk=Tk()
m=Message(text="Hover on Button to show Balloonhelp, close window to quit")
m.pack(padx=10, pady=10)
b=Button(text="OK")
b.pack(padx=100, pady=100)
w=Balloonhelp(delay=100, background="#fcf87f", place="left", offset=3)
w.help_message(b, "display\n  tooltips")
tk.mainloop()
