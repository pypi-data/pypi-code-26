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

* show(GStream) converts the graphic stream to pdf, svg or other
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


import os
import numpy as np
from . import command
from . import myfont
from . import makepdf
"""
    LUKIS stream : csv format
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    command,parameter,...parameter EOL
    :
    :
    command,parameter,...parameter EOL
"""
"""
    Color setting
    ~~~~~~~~~~~~~
    Follow the method used in pdf to set the
    -color of stroking- and the -color of nonstroking-
"""
#Global constants
SPACE = " "
TAB = " "*4
COMMA = ","
QUOTE = "\""
QUOTE_SINGLE = "\'"
EOL = "\n"

# Global parameters. Use them cautiously.
_Current_FillColor_ = (0, 0, 0)
_Current_LineColor_ = (0, 0, 0)
_Current_LineWidth_ = 1
_Current_FontSize_ = 12
_Current_Font_ = "Helvetica"
_DEFAULT_PAPER_ = (500,400) #(width, height)

class font:
    Times_Roman           = "Times-Roman"
    Times_Bold            = "Times-Bold"
    Times_Italic          = "Times-Italic"
    Times_BoldItalic      = "Times-BoldItalic"
    Helvetica             = "Helvetica"
    Helvetica_Bold        = "Helvetica-Bold"
    Helvetica_Oblique     = "Helvetica-Oblique"
    Helvetica_BoldOblique = "Helvetica-BoldOblique"
    Courier               = "Courier"
    Courier_Bold          = "Courier-Bold"
    Courier_Oblique       = "Courier-Oblique"
    Courier_BoldOblique   = "Courier-BoldOblique"
    Symbol                = "Symbol"
    Symbol_ZapfDingbats   = "ZapfDingbats"

def getcurrent_fillcolor():
    return _Current_FillColor_
def getcurrent_linecolor():
    return _Current_LineColor_

def form(*parameters):
    """
    string form( * string)

    write the arguments in the LUKIS stream format
    e.g.
        form("lineto", "1", "2") ==> "lineto,1,2\n"
    """
    S = ""
    for i in range(len(parameters)):
        S += parameters[i]
        if i < len(parameters) - 1:
            S += COMMA
    S+= EOL
    return S

def ftos (Float_Value):
    """
    string ftos(float)

    convert float to string
    Instead of using python's ftos(), use this one to control the precision
    my Float to String mini function

    Precision = %.4f
    Unnecessary 0 will be discarded
    """
    S= "%.4f" %Float_Value
    n = len(S)
    if S[n-5] == '.' :
        if S[ n-4 : n ] =="0000":
            S = S[ 0 : n-5 ]
        elif S[n-3:n] == "000":
            S = S[ 0 : n-3]
        elif S[n-2:n] == "00":
            S = S[ 0 : n-2]
        elif S[n-1] == "0":
            S = S[ 0 : n-1]
    return S

# ----------------------------------------------------
# Basic and generic building block
def lineto(x, y):
    """
    lineto(x,y) creates a new point at (x,y)
    and make a line path to that point.

    Example
    ~~~~~~>
    #draw a simple line
    S = moveto(50,50)
    S += lineto(150,150)
    S += stroke()
    show(S)
    # End of Example

    """
    return form(command.LineTo, ftos(x), ftos(y) )

def moveto(x, y):
    """
    moveto(x,y) moves the path to (x,y) without creating a line.
    """
    return form(command.MoveTo, ftos(x), ftos(y) )

def curveto(x1, y1, x2, y2, x3, y3):
    """
    curveto(x1, y1, x2, y2, x3, y3) create a three points Bezier curve.
    """
    return form(command.CurveTo,
                ftos(x1),
                ftos(y1),
                ftos(x2),
                ftos(y2),
                ftos(x3),
                ftos(y3)
                )

def stroke():
    """
    stroke() draws the line for the defined paths
    """
    return form(command.Stroke)

def close():
    return form(command.Close)

def close_stroke():
    return form(command.Close_Stroke)

def fill():
    return form(command.Fill)

def close_fill_stroke():
     return form(command.Close_Fill_Stroke)

def fill_stroke():
    return form(command.Fill_Stroke)

def translate_coordinate(x, y):
    """
    Translate the coordinate to x,y
    """
    return form(command.Translate, ftos(x), ftos(y))

def rotate_coordinate(angle):
    return form(command.RotateCoordinate,
                ftos(angle)
                )
def scale(S, scalex=1, scaley=1):
    if scalex == 1 and scaley == 1:
        return S
    return form(command.Scale, ftos(scalex), ftos(scaley))\
            + S\
            + form(command.Scale, "1", "1")

def setlinecolor(R, G, B):
    """
    R, G, B are decimals from 0 ~ 255
    """
    global _Current_LineColor_
    _Current_LineColor_ = (R,G,B)
    return form(command.SetLineColor,
                ftos(R),
                ftos(G),
                ftos(B))
def setfillcolor(R, G, B):
    """
    R, G, B are decimals from 0 ~ 255

    P.S. Fill color is also the font color for text
    """
    global _Current_FillColor_
    _Current_FillColor_ = (R,G,B)
    return form(command.SetFillColor,
                ftos(R),
                ftos(G),
                ftos(B))
def setlinewidth(linewidth):
    global _Current_LineWidth_
    _Current_LineWidth_ = linewidth
    return form(command.SetLineWidth, ftos(linewidth) )
def insertpicture(x,y,width, height, filename):
    """
    Insert the picture by filename
    x : x in pt
    y : y in pt
    width : the width of the picture
    height : the height of the picture
    """
    return form(command.Picture,
                ftos(x),
                ftos(y),
                ftos(width),
                ftos(height),
                QUOTE + filename + QUOTE)


# ----------------------------------------------------
# Non generic translation
def rotate(S, angle, dx = 0, dy = 0):
    """
    Rotates the object S for an angle (degree) about point (dx, dy)
    """
    if dx == 0 and dy == 0:
        return rotate_coordinate(angle)\
                + S\
                + rotate_coordinate(-angle)
    S = move(S, -dx, -dy)
    S = rotate(S, angle, 0, 0)
    S = move(S, dx, dy)
    return S

def move(S, x, y):
    """
    Move the object defined in S to x,y
    """
    return translate_coordinate(x,y)\
            + S\
            + translate_coordinate(-x, -y)



def line(x1, y1, x2, y2):
    return moveto(x1, y1)\
            + lineto(x2, y2)\
            + stroke()

def circle(x, y, radius, border = True, solid = True):
    magic = 0.551915024494
    S = ""
    S = moveto(    x, y + radius )

    S += curveto(
                x + magic*radius,
                y + radius,
                x + radius,
                y + magic*radius,
                x + radius,
                y + 0)

    S += curveto(
                x + radius,
                y - 1.0*magic*radius,
                x + magic*radius,
                y - 1.0*radius,
                x + 0,
                y - 1*radius)

    S += curveto(
                x - 1.0*magic*radius,
                y - 1*radius,
                x - 1.0*radius,
                y - 1*magic*radius,
                x - 1*radius,
                y + 0)

    S += curveto(
                x - 1*radius,
                y + magic*radius,
                x - 1*magic*radius,
                y + radius,
                x + 0,
                y + radius)

    if solid == True:
        if border == True:
            S += fill_stroke()
        else:
            S += fill()
    else:
        if border == True:
            S += stroke()
        else:
            pass
    return S

def rectangle(x1, y1, x2, y2, border = True, solid = True):
    S = moveto(x1, y1)\
        + lineto(x2, y1)\
        + lineto(x2, y2)\
        + lineto(x1, y2)\
        + close()
    if solid == True:
        if border == True:
            S += fill_stroke()
        else:
            S += fill()
    else:
        if border == True:
            S += stroke()
        else:
            pass
    return S

def setfont(font, fontsize):
    global _Current_Font_
    _Current_Font_ = font
    global _Current_FontSize_
    _Current_FontSize_ = fontsize
    return form(
            command.SetFont,
            font,
            ftos(fontsize)
            )
def text(x,y, thetext):
    """
    -------------------
    Put a text at (x,y)
    -------------------

    Example:
    ~~~~~~~>
    # Simple Text
    S = setfont("Helvetica", 16)
    S += text(100,200, "This is Helvetica font size = 16")
    S += setlinecolor(30,30,30)\
         + setlinewidth(0.5)
    S += line(100, 200, 400, 200)
    S += setfont("Times-Roman", 12)
    S += text(100, 100, "This is Time regular")
    S += line(100, 100, 400, 100)
    show(S)
    # End of Example
    """
    return form(command.Text,
            ftos(x),
            ftos(y),
            QUOTE + thetext + QUOTE,
            )
def ftext(x,y,thetext, alignment = 0, rotation = 0, font = None, fontsize = None):
    """
    ---------------------------------------------------
    Create formated text. Allow Rotation, and Alignment
    ---------------------------------------------------

    x, y     : The origin position
    alignment:
            0   -> left aligned
            0.5 -> center aligned
            1   -> right aligned
            p.s. Also allows non-zero values
    rotation : angle in degree
    font     : font to be set for the use only in this function,
               i.e. the current font will be set to this font,
                    and then reset back after use.
                Use the current font if None
    fontsize : fontsize to be set for the use only in this function,
               i.e. the current fontsize will be set to this font,
                    and then reset back after use.
                Use the current fontsize if None

    Example
    ~~~~~~~>
    # Rotation of text
    L = line(100, 200, 300, 200)
    S = setfont("Helvetica", 16)
    S += ftext(100,200, "Hello", 0, 45)
    S += setfont("Times-Roman", 14)
    S += text(150, 220, "45 degree")
    S += setlinecolor(200,0,0)\
            + setlinewidth(0.5)
    S += L
    S += rotate( L, 45, 100, 200)
    show(S)
    # End of Example

    Example:
    ~~~~~~~>
    # Alignment of text
    L =  setlinewidth(0.4)\
        + setlinecolor(0, 100, 0)\
        + line(100, 100, 300, 100)\
        + line(100, 200, 300, 200)\
        + line(100, 300, 300, 300)\
        + line(200, 100, 200, 300)
    T =   ftext(200,100,"Helvetica14 (align = 0)", 0, 0, "Helvetica", 14)\
        + ftext(200,200,"Times-Bold13 (align = 0.5)", 0.5, 0, "Times-Bold", 13)\
        + ftext(200,300,"Courier12 (align = 1.0)", 1, 0, "Courier", 12)

    Caption = setfillcolor(255, 0, 0)\
              + ftext(100,350, "Alignment: xo = xo - alignment*(text width)")
    show(L + T + Caption)
    # End of Example
    """
    S =""
    xo = 0
    yo = 0

    if font is not None:
        Backup_Font = _Current_Font_
        Backup_FontSize = _Current_FontSize_
        if fontsize is not None:
            S += setfont(font, fontsize)
        else:
            S += setfont(font, _Current_FontSize_)

    else:
        if fontsize is not None:
            Backup_Font = _Current_Font_
            Backup_FontSize = _Current_FontSize_
            S += setfont(_Current_Font_, fontsize)
        else:
            pass

    if alignment != 0:
        xo = xo - alignment * \
            myfont.GetStringWidth(thetext,
                                    _Current_Font_,
                                    _Current_FontSize_)
    S += text(xo,yo, thetext)
    if rotation != 0:
        S = rotate(S, rotation)
    S = move(S, x, y)

    #Clean up
    if font is None and fontsize is None:
        pass
    else:
        S += setfont(Backup_Font, Backup_FontSize)
    return S

def put(symbol, x,y,rotation=0, scalex = 1, scaley=1):
    """
        Put the symbol, or text, or graphics defined in valid LUKIS stream
        at x, y, with rotation and scale
    """
    return move(
                rotate(
                    scale(symbol, scalex, scaley),
                    rotation),
                x, y)


def show(LukisStream,
        papersize = _DEFAULT_PAPER_,
        show=True,
        format = "pdf",
        filename = "lukis.pdf",
        viewer = "open"):
    """
    Convert the lukis stream to the defined format and store it in the
    filename.
    Open the file using the defined viewer if show == True

    LukisStream : The string stream that contains valid graphic defination
    papersize : The size of the output graphics
                Allow two input formats:
                papersize = "A4"
                papersize = (400, 500)
                            (WIDTH, HEIGHT)
    """
    makepdf.makepdf(
        LukisStream,
        PaperSize=papersize,
        PDF_Filename = filename
        )
    if show:
        os.system(viewer + " " + filename)

    return
