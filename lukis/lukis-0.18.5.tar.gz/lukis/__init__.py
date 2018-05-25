#!python3
"""
=====
Lukis
=====

Description:
~~~~~~~~~~~~
* Generate device independent vector graphic stream
  that can be converted to pdf, svg, or other vector graphic format.

* The output stream is in pure txt, and csv format.

* A simple stream looks like this::

    MoveTo,50,50
    LineTo,150,150
    Stroke

* "Lukis" is the Malay word for "Draw"

* show(GStream) generates convert the graphic stream to pdf or svg or other
  graphic file, and open it using the default viewer.

Example:
--------
::

    #To make a line from (0,0) to (300,300) and display the graphics:
    S = moveto(0,0)\\
    + lineto(300,300)\\
    + stroke()
    show(S)


Installation
~~~~~~~~~~~~
Python 3 as default Python::

	pip install lukis

Python as Python3::

	pip3 install kopi


Coding habits:
--------------
* For fixed/static length array inputs like (width, height), (origin_x, origin_y) etc,
  uses tuple (__, __)
* For dynamic length array like [x0, x1, x2, ...xn],
  use list or numpy array [__, __, ...]

"""
__all__ = ["lineto", "moveto", "curveto", "stroke", "show",
            "line","setlinewidth", "setlinecolor",
            "setfillcolor",
            "move", "rotate",
            "setfont", "text", "ftext",
            "rectangle"]
__version__ = "0.18.5"

from .lukis import *
