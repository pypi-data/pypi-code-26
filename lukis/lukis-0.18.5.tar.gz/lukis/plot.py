#!python3
"""
    ====
    Plot
    ====
    A standalone light module to plot simple 2D gragh.
    It relied on using lukis.py.


    Example :
    ~~~~~~~~
    # plot simple line

    ~ End of example ~
"""
import numpy as np
from . import lukis as lk
from . import mypretty
from . import myfont
__all__ = ["plot", "example1"]

_PlotSize_ = (350, 260)
_Origin_ = [80,80]
_DEFAULT_PAPER_ = (500,400)
# Commands that are reused from lukis.py
def setlinewidth(linewidth):
    return lk.setlinewidth(linewidth)
def setlinecolor(R, G, B):
    return lk.setlinecolor(R, G, B)
def setfillcolor(R, G, B):
    return lk.setfillcolor(R, G, B)
def show(LukisStream,
        papersize = _DEFAULT_PAPER_,
        show=True,
        format = "pdf",
        filename = "lukis.pdf",
        viewer = "open"):
    return lk.show(LukisStream,
            papersize ,
            show,
            format,
            filename,
            viewer)
def pretty(data_array):
    return mypretty.pretty(data_array)

def PosValueOnly(value):
    return value if value > 0 else 0


def map2pt(array, tickmin, tickmax, origin, length_pt):
    v_pt_o = origin
    v_pt = v_pt_o + (array - tickmin)/(tickmax - tickmin)*length_pt
    return v_pt
def mapXY2pt(xarray, yarray,
        xmin, xmax, ymin, ymax,
        plotsize = _PlotSize_,
        origin = _Origin_):
    # just in case
    xarray = np.array(xarray)
    yarray = np.array(yarray)
    (plotwidth, plotheight) = plotsize
    (origin_x, origin_y) = origin

    x_pt = map2pt(xarray, xmin, xmax, origin_x, plotwidth)
    y_pt = map2pt(yarray, ymin, ymax, origin_y, plotheight)
    return (x_pt, y_pt)
def plot(xarray, yarray,limit,plotsize = _PlotSize_,origin = _Origin_):
    (xmin, xmax, ymin, ymax) = limit
    (x_pt, y_pt) = mapXY2pt(xarray, yarray,
                            xmin, xmax,
                            ymin, ymax,
                            plotsize,
                            origin)
    S = ""
    S += lk.moveto(x_pt[0], y_pt[0])
    for i in range(len(xarray)-1):
        if xarray[i] >= xmin and xarray[i] <= xmax:
            S += lk.lineto(x_pt[i+1], y_pt[i+1])
    S += lk.stroke()
    return S
def point(xarray, yarray, size, limit, plotsize = _PlotSize_,origin = _Origin_):
    (xmin, xmax, ymin, ymax) = limit
    (x_pt, y_pt) = mapXY2pt(xarray, yarray,
                            xmin, xmax,
                            ymin, ymax,
                            plotsize,
                            origin)
    S = ""
    for i in range(len(x_pt)):
        x = x_pt[i]
        y = y_pt[i]
        S += lk.circle(x, y, size, border = True, solid = True)
    return S
def axis(axisnumber, tickarray,
            label = "",
            ticklength = 6,
            plotsize = _PlotSize_,
            origin = _Origin_,
            font = "Helvetica",
            fontsize = 8,
            labelfont = "Helvetica",
            labelfontsize = 12,
            offset = 0):
    (plotwidth, plotheight)  = plotsize
    (origin_x, origin_y) = origin

    S = ""
    if axisnumber == 0:
        # lower X axis
        S += lk.line(origin_x,
                    origin_y - offset,
                    origin_x + plotwidth,
                    origin_y - offset
                    )
    elif axisnumber == 1 :
        # left Y axis
        S += lk.line(origin_x  - offset,
                    origin_y,
                    origin_x - offset,
                    origin_y + plotheight
                    )
    elif axisnumber == 2 :
        # upper X axis
        S += lk.line(origin_x,
                    origin_y + plotheight + offset,
                    origin_x + plotwidth,
                    origin_y + plotheight + offset
                    )
    elif axisnumber == 3 :
        # right Y axis
        S += lk.line(origin_x + plotwidth + offset,
                    origin_y,
                    origin_x + plotwidth + offset,
                    origin_y + plotheight
                    )
    #Draw tick
    if axisnumber == 0 or axisnumber == 2 :
        XorY = 0
    else:
        XorY = 1

    ta_pt = map2pt(tickarray,
                    tickmin = tickarray[0],
                    tickmax = tickarray[-1],
                    origin = origin[XorY],
                    length_pt = plotsize[XorY])

    S += lk.setfont(font, fontsize)
    if axisnumber == 0:
        for i in range(len(ta_pt)):

            S += lk.line(ta_pt[i],
                        origin_y - offset,
                        ta_pt[i],
                        origin_y - ticklength - offset)
            S += lk.ftext(ta_pt[i],
                        origin_y - PosValueOnly(ticklength) - fontsize - offset,
                        thetext = str(tickarray[i]),
                        alignment = 0.5
                        )
        # The label
        S += lk.ftext(  origin_x + plotwidth/2,
                        origin_y  -  PosValueOnly(ticklength) - offset - fontsize - labelfontsize,
                        thetext = label,
                        alignment = 0.5,
                        font = labelfont,
                        fontsize = labelfontsize)
    elif axisnumber == 1:
        LongestTickValue = 0
        for i in range(len(ta_pt)):
            TickText = str(tickarray[i])
            S += lk.line(origin_x - offset,
                        ta_pt[i],
                        origin_x - ticklength -offset,
                        ta_pt[i])
            S += lk.ftext(origin_x - PosValueOnly(ticklength) - 0.3*fontsize -offset,
                        ta_pt[i] - fontsize*0.25,
                        thetext = TickText,
                        alignment = 1)
            ThisTickTextWidth = myfont.GetStringWidth(TickText, labelfont, labelfontsize)
            if ThisTickTextWidth > LongestTickValue:
                LongestTickValue = ThisTickTextWidth

        # The label
        S += lk.ftext(  origin_x -  PosValueOnly(ticklength) - offset - LongestTickValue,
                        origin_y  +  plotheight/2,
                        thetext = label,
                        alignment = 0.5,
                        rotation = 90,
                        font = labelfont,
                        fontsize = labelfontsize)
    elif axisnumber == 2:
        for i in range(len(ta_pt)):
            S += lk.line(ta_pt[i],
                        origin_y + plotheight + offset,
                        ta_pt[i],
                        origin_y + ticklength + plotheight + offset)
            S += lk.ftext(ta_pt[i],
                        origin_y + plotheight + PosValueOnly(ticklength) + 0.3*fontsize + offset,
                        thetext = str(tickarray[i]),
                        alignment = 0.5
                        )
            # The label
            S += lk.ftext(  origin_x + plotwidth/2,
                            origin_y  + PosValueOnly(ticklength) + offset + fontsize,
                            thetext = label,
                            alignment = 0.5,
                            font = labelfont,
                            fontsize = labelfontsize)
    elif axisnumber == 3:
        for i in range(len(ta_pt)):
            S += lk.line(origin_x + plotwidth + offset,
                        ta_pt[i],
                        origin_x + ticklength + plotwidth + offset,
                        ta_pt[i])
            S += lk.ftext(origin_x + plotwidth + ticklength + 0.3*fontsize + offset,
                        ta_pt[i] - fontsize*0.25,
                        thetext = str(tickarray[i]),
                        alignment = 0
                        )

    return S
def plotbox(plotsize = _PlotSize_, origin = _Origin_, color = (220,220,220) ):
    PreviousFillColor = lk.getcurrent_fillcolor()
    PreviousLineColor = lk.getcurrent_linecolor()
    S = ""
    S += lk.setfillcolor(color[0], color[1], color[2])
    x1 = origin[0]
    y1 = origin[1]
    x2 = x1 + plotsize[0]
    y2 = y1 + plotsize[1]
    S += lk.rectangle(x1, y1, x2, y2, border = False, solid = True)
    return S
def grid(axisnumber, tickarray, plotsize = _PlotSize_,origin = _Origin_):
    (origin_x,origin_y) = origin
    if axisnumber == 0:
        XorY = 0
    else:
        XorY = 1

    ta_pt = map2pt(tickarray,
                    tickmin = tickarray[0],
                    tickmax = tickarray[-1],
                    origin = origin[XorY],
                    length_pt = plotsize[XorY])
    S =""
    for i in range(len(ta_pt)):
        if axisnumber == 0:
            PlotHeight = plotsize[1]
            S += lk.line(ta_pt[i],
                        origin_y,
                        ta_pt[i],
                        origin_y + PlotHeight)

        elif axisnumber == 1:
            PlotWidth = plotsize[0]
            S += lk.line(origin_x,
                        ta_pt[i],
                        origin_x + PlotWidth,
                        ta_pt[i])
    return S

def example1():
    X1 = np.linspace(0, 5, 10)
    Y0 = X1
    Y1 = X1**2
    Y2 = X1**3

    # Set the plot limit using pretty
    # They can also be set manuallu too.
    xtick= pretty(X1)
    ytick= pretty(Y2)
    (xmin, xmax) = (xtick[0], xtick[-1])
    (ymin, ymax) = (ytick[0], ytick[-1])
    limit = (xmin, xmax, ymin, ymax)

    S = ""

    # Draw the plot background
    S += plotbox()
    S += setlinewidth(0.5)
    S += setlinecolor(255,255,255)
    S += grid(0, xtick)
    S += grid(1, ytick)


    #Plot the first curve, and put the data points
    S += setlinecolor(0,150,0)
    S += setfillcolor(0,260,0)
    S += plot(X1, Y0, limit)
    S += point(X1, Y0, size = 3, limit = limit)

    #On the same plot, draw the second curve
    S += setlinecolor(150,0,0)
    S += setfillcolor(220,0,0)
    S += plot(X1, Y1, limit)
    S += point(X1, Y1, size = 3, limit = limit)

    #On the same plot, draw the second curve
    S += setlinecolor(0,0,150)
    S += setfillcolor(0,0,260)
    S += plot(X1, Y2, limit)
    S += point(X1, Y2, size = 3, limit = limit)

    #Draw the axies
    S += setlinecolor(0,0,0)
    S += setfillcolor(0,0,0)
    S += axis(0, xtick, label = "xlabel", offset = 10)
    S += axis(1, ytick, label = "ylabel", offset = 10)
    S += axis(2, xtick, offset = 5)
    S += axis(3, ytick, offset = 5)
    show(S)
