""" General setup for plot
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

__all__ = ['colors',
           'colors_default',
           'myplot_style',
           'color_list',
           'colored',
           'bcolors',
           ]

__date__ = '01/04/2018'
__version__ = '0.2.0'
__author__ = 'J.G. Chen'
__email__ = 'cjgls@pku.edu.cn'

from cycler import cycler
import matplotlib.pyplot as plt

# constant vars
colors = ['k', 'r', 'g', 'b', 'c', 'm', 'y', 'lime',
          'darkviolet', 'pink', 'darkred', 'mediumslateblue']
"""Color list

mpl.rcParams['axes.prop_cycle'] = cycler(color=colors)

"""
colors_default = [u'#1f77b4', u'#ff7f0e', u'#2ca02c', u'#d62728', u'#9467bd',
                  u'#8c564b', u'#e377c2', u'#7f7f7f', u'#bcbd22', u'#17becf']
"""Default color list

mpl.rcParams['axes.prop_cycle'] = cycler(color=colors)

"""

# rcParams.keys()   --> check keys for plot style
# plt.tick_params()
myplot_style = {'font.size': 32,
                # 'font.weight': 'bold',
                'legend.fontsize': 32,
                'legend.labelspacing': 0.1,
                # 'legend.frameon': False,
                'figure.figsize': (10, 8),
                'lines.linewidth': 3,
                'lines.markersize': 8,
                'xtick.direction': 'out',
                'xtick.major.size': 12,
                'xtick.minor.visible': True,
                'xtick.minor.size': 8,
                'xtick.minor.width': 2,
                'xtick.major.width': 2,
                'ytick.direction': 'out',
                'ytick.major.size': 12,
                'ytick.minor.visible': True,
                'ytick.minor.size': 8,
                'ytick.minor.width': 2,
                'ytick.major.width': 2,
                'figure.facecolor': 'white',
                # 'savefig.dpi':200,
                # NOTE: change dpi may result in difference
                #       between saved figure and plot
                'savefig.bbox': 'tight'
                }
"""Change matplotlib.pyplot figure style

plt.style.use(myplot_style)

"""

class bcolors:
    """ Builtin color format.

    Notes
    -----
    usage: bcolors.HEADER.format('target text')

    """

    HEADER = '\033[95m{}\033[0m'
    OKBLUE = '\033[94m{}\033[0m'
    OKGREEN = '\033[92m{}\033[0m'
    WARNING = '\033[93m{}\033[0m'
    FAIL = '\033[91m{}\033[0m'
    ENDC = '\033[0m'
    BOLD = '\033[1m{}\033[0m'
    UNDERLINE = '\033[4m{}\033[0m'

def colored(text, style=0, fg=30, bg=49, fstr=None, **kwgs):
    """ generate colored text for terminal.

    Parameters
    ----------
    text: str
    style: int, 0 to 7, optional, default: 0
    fg: int, 30 to 37, optional, default: 30
        foreground color
    bg: int, 40 to 49, optional, default: 49
        background color, use current bg color by default.
    fstr: str, optional, default: None
        format code string, which will be used by `fstr`.format(`text`).
        e.g. '\033[91m{}\033[0m', or '\x1b[0;30;49m{}\x1b[0m'.

    """

    if fstr:
        return fstr.format(text)
    format_code = ';'.join([str(style), str(fg), str(bg)])
    return '\x1b[{}m{}\x1b[0m'.format(format_code, text)


def color_list(n=10, cmap='jet', reverse=False):
    """Generate a color list from color map ``cmap``.

    Parameters
    ----------
    n : int, optional, default is 10.
        Size of color list returned.
    cmap : str, optional,
        Standard color map name
        http://matplotlib.org/examples/color/colormaps_reference.html
    reverse : Bool, optional, default: False
        Reverse the color list.

    Notes
    -----
    tips for change color cycle in plotting multi-lines

    >>> from cycler import cycler
    >>> import matplotlib as mpl
    >>> mpl.rcParams['axes.prop_cycle'] = cycler(color=colors)

    Returns
    -------
    colors : list
        a color list, size = n, each element is composited by
        a tuble(r, g, b, a)

    See Also
    --------
    :class:`matplotlib.colors.LinearSegmentedColormap`
    :class:`matplotlib.colors.ListedColormap`

    """

    cm = plt.get_cmap(cmap)
    colors = [cm(1.0 * i / (n - 1)) for i in range(n)]
    if reverse:
        colors.reverse()
    return colors
