"""Field class
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

__all__ = ['Field']

__date__ = '10192017'
__version__ = '0.1.2'
__author__ = 'J. G. Chen'
__email__ = 'cjgls@pku.edu.cn'

import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.axes_grid1 import make_axes_locatable


# test animation writer for movies
try:
    # using system's ffmpeg
    animation.writers['ffmpeg']
except:
    # using ~/bin/ffmpeg
    # conda install -c conda-forge ffmpeg
    # or download from
    # github.com/imageio/imageio-binaries/tree/master/ffmpeg
    ffmpeg = os.path.join(os.path.dirname(__file__),
                          "../bin/ffmpeg")
    plt.rcParams['animation.ffmpeg_path'] = ffmpeg

# global vars
_pause = False


def _onclick(event, anim):
    """Pause/continue animation by mouse event

    Parameters
    ----------
    event: :class:`matplotlib.backend_bases.Event`
    anim: :class:`matplotlib.animation.FuncAnimation`

    Notes
    -----
    using ``lambda`` function to pass the `arguments` to this function:
        mpl_connect('button_press_event', lambda event: _onclick(event, anim))

    """

    global _pause
    _pause ^= True
    if _pause:
        anim.event_source.stop()
    else:
        anim.event_source.start()


def _cal_lim(data, percent=0.05):
    """ calculate data limit for axis-limit in plot

    Parameters
    ----------
    data: data in any type
    percent: scalar, >= 0, [default: 0.05]
        extend the limit in both side by `percent` of total range
        if percent < 0, auto-reset to 0

    Retruns
    -------
    ret: list
        [min, max]

    Notes
    -----
    if max(data) == min(data), then
        ret = [min-0.05*min, min+0.05*min]
        (ret = [min-1, min+1] if min=0)

    Examples
    --------
    >>> data = [0, 1]
    >>> _cal_lim(data, 0.5)
    # [-0.5, 1.5]
    >>> data = [1, 1]
    >>> _cal_lim(data, 0.5)
    # [0.9499999999999996, 1.05]

    """

    dmin, dmax = np.min(data), np.max(data)
    length = dmax - dmin    # length >= 0
    if percent < 0:
        percent = 0
    extend = length * percent
    if length <= 0:
        # dmax = dmin
        extend = 0.05 * np.abs(dmax) if np.abs(dmax) > 0 else 1
    return [dmin - extend, dmax + extend]


class Field(np.ndarray):
    """Field(data, dtype=None, copy=True)

    Methods
    -------
    moment_xyzt(axis=-1)
        return (dc, rms) parts at axis=`axis`.
    dc(axis=-1)
        return dc parts at axis=`axis`.
    rms(axis=-1)
        return rms parts at axis=`axis`.
    normalize(norm=None)
        data normalized by `norm` if `norm` is given, otherwise `maximum` used.
    plot(\*arg, \*\*kwargs)
        plot line(s) or animated lines for 1D/2D data.
    contourf(\*args, \*\*kwargs)
        plot (animated) contour/contourf/surface plot for 2D/3D data.
    showdata(\*args, \*\*kwargs)
        Visualiaztion and animation for 1/2/3D data.

    """

    __array_priority__ = 100000

    def __new__(subtype, data, dtype=None, copy=True, order=None, subok=False,
                ndmin=0):
        if isinstance(data, Field):
            dtype2 = data.dtype

            if (dtype is None):
                dtype = dtype2

            if (dtype2 == dtype) and (not copy):
                return data

            if type(data) is not subtype and not(subok and
                                                 isinstance(data, subtype)):
                data = data.view(subtype)

            return np.array(data, dtype=dtype, copy=copy, order=order,
                            subok=True, ndmin=ndmin)

        if isinstance(data, np.ndarray):
            if dtype is None:
                intype = data.dtype
            else:
                intype = np.dtype(dtype)

            new = data.view(subtype)
            if intype != data.dtype:
                return new.astype(intype)

            if copy:
                return new.copy()
            else:
                return new

        ret = np.array(data, dtype=dtype, copy=copy, order=order,
                       subok=True, ndmin=ndmin).view(subtype)
        return ret

    def __array_wrap__(self, obj):
        """Called after ufuncs to do cleanup work. """

        # if ufunc output is scalar, return it
        if obj.shape == ():
            return obj[()]
        else:
            return np.ndarray.__array_wrap__(self, obj)

    def __array_finalize__(self, obj):
        pass

    '''
    WARNING:
        This operator overload change the rules of numpy.ndarray operation.
    See Also: Broadcasting of numpy
    It can be achieved by 'self + other[:, :, None]' without overload operator
    # overload operator +, -
    def __add__(self, other):
        """ overload add function for case
            self.shape[:-1] = other.shape

        Examples
        --------
        >> a = Field(np.arange(2*3).reshape(2,3))
        >> b = np.asarray([10, 10])
        >> a.shape
        (2, 3)
        >> b.shape
        (2,)
        >> a+b
        Field([[10, 11, 12],
               [13, 14, 15]])
        """
        # sort dimension size
        sdata, ldata = ((self, np.asarray(other))
                        if np.asarray(other).ndim > self.ndim
                        else (np.asarray(other), self))
        sshape, lshape = sdata.shape, ldata.shape

        # if they are in same shape, or one is just a scalar
        if sshape == lshape or len(sshape) == 0:
            ret = self.view(np.ndarray) + np.asarray(other)
        elif lshape[:-1] == sshape:
            ret = np.asarray(ldata) + np.tile(
                np.reshape(sdata, sshape+(1,)),
                lshape[-1])
        else:
            raise ValueError("operands could not be broadcast together with "
                             "shapes {} {}".format(self.shape,
                                                   np.asarray(other).shape))
        return ret.view(Field)

    def __sub__(self, other):
        return self + (-other)

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        return -self + other

    def __iadd__(self, other):
        return self + other

    def __isub__(self, other):
        return self + (-other)
    '''

    def moment_xyzt(self, axis=-1):
        """return (dc, rms) parts at axis=`axis`.
        """

        return self.mean(axis=axis).squeeze(), self.std(axis=axis).squeeze()

    def dc(self, axis=-1):
        """return dc part at axis=`axis`. """

        return self.mean(axis=axis)

    def rms(self, axis=-1):
        """return rms part at axis=`axis`. """

        return self.std(axis=axis)

    def normalize(self, norm=None):
        """return normalizaed array.

        Parameters
        ----------
        norm : float, optional
            return result normalized to ``norm`` if it is given, otherwise
            result is normalized to maximum value by default.
        """

        if not isinstance(norm, (int, float)):
           norm = self.max()
        return self/float(norm)

    def plot(self, *args, **kwargs):
        """plot line(s) or animated lines for 1D/2D data

        Parameters
        ----------
        kind: str, optional, default: 'surface'
            work for 2D data
            ['m', 'mlines', 'multilines']: multi-lines in one figure
            'animation': animated lines
        newfig: bool, optional, default: True
            if Ture[default], create new figure,
            otherwise, plot on current figure and axes
        x/ylabel: str, optional, default: None
            labels for x/y-axis,
        xlim: 2-elements data, optional, default: None
            axis limit for x-axis
        ylim: [2-elements data | 'fixed'], optional, default: None
            axis limit for y-axis
            'fixed': automatically set the ylim according to the data limit.
        title: str, optional, default: None
            figure title
            in animation, it is passed to 'title.format(frame_number)'
            or 'index = {}".format(frame_number) if it is None.
        grid: bool, optional, default: True
            grid on if True.
        output: str, optional, default: None
            filename to store the figure or animation. It should include
            suffix. '.gif' format is recommended.

        **key-word arguments for 2D data**:
        index: int | array_like, default: 1

            - array_like: only using data[:, index] for animation.
            - int: only using data[:, ::index] for animation, the last
                frame is included as well.

        **key-word argments for animation**:
        interval: int, optional, default: 20
            delay between frames in milliseconds.
        fps: number, optional, default: 5
            frames per second in the movie.
        metadata: dict, optional, default: {artist:$USER}
            Dictionary of keys and values for metadata to include in the
            output file. Some keys that may be use include:
            title, artist, genre, subject, copyright, srcform, comment.
        bitrate: number, optional, default: -1
            Specifies the number of bits used per second in the compressed
            movie, in kilobits per second. A higher number means a higher
            quality movie, but at the cost of increased file size.
            -1 means let utility auto-determine.

        Returns
        -------
        ret: figure object|animation object

        See Also
        --------
        :func:`matplotlib.pyplot.plot`

        """

        # create new fig?
        newfig = kwargs.pop('newfig', True)
        if newfig:
            fig, ax = plt.subplots()
        else:
            fig = plt.gcf()
            ax = plt.gca()

        # auto squeeze array
        ndim = self.squeeze().ndim
        if ndim not in [1, 2]:
            raise ValueError("ERROR: only 1D/2D data supported.")
            return None
        xsize = self.squeeze().shape[0]
        # xdata for x-axis
        x = kwargs.pop('x', None)
        if x is None:
            x = np.arange(xsize)

        # properties of fig
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        xlim = kwargs.pop('xlim', None)
        ylim = kwargs.pop('ylim', None)
        title = kwargs.pop('title', None)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        if xlim:
            ax.set_xlim(xlim)
        if ylim == 'fixed':
            ax.set_ylim(_cal_lim(self))
        elif isinstance(ylim, (list, tuple, np.ndarray)):
            ax.set_ylim(ylim)
        if title:
            ax.set_title(title)

        grid = kwargs.pop('grid', True)
        if grid:
            ax.grid()

        # save fig/animation to as `output`
        output = kwargs.pop('output', None)
        # animation or multi-lines for 2D data
        kind = kwargs.pop('kind', 'animation')

        # TODO: output option
        #       animation along selected axis??
        #       or axis=-1 by default

        # plot line
        if ndim == 1:
            ret = ax.plot(x, self.squeeze(), *args, **kwargs)
            if output:
                plt.tight_layout()
                fig.savefig(output)
            return ret

        # animation[default]/multi-lines
        if ndim == 2:
            index = kwargs.pop('index', 1)
            ysize = self.squeeze().shape[1]
            if isinstance(index, int):
                index = range(0, ysize, index)
                # include last step
                if index[-1] != ysize - 1:
                    index.append(ysize - 1)

            # options for animation
            interval = kwargs.pop('interval', 20)
            fps = kwargs.pop('fps', 5)
            metadata = kwargs.pop('metadata', dict(artist=os.environ['USER']))
            bitrate = kwargs.pop('bitrate', -1)

            # multi-lines
            if kind in ['m', 'mlines', 'multilines']:
                ret = ax.plot(x, self.squeeze()[:, index], *args, **kwargs)
                ax.legend(index, loc=0)
                return ret

            # animation [default]
            line, = ax.plot([], [], *args, **kwargs)
            if xlim is None:
                ax.set_xlim(_cal_lim(x))

            # initialization function: plot the background of each frame
            def init():
                line.set_data([], [])
                return line,

            # animation function: This is called sequentially
            def animate(i):
                # update title, xlim, ylim and line
                if ylim == 'fixed':
                    ax.set_ylim(_cal_lim(self[:, index]))
                elif isinstance(ylim, (list, tuple, np.ndarray)):
                    ax.set_ylim(ylim)
                else:
                    ax.set_ylim(_cal_lim(self[:, i]))
                ax.set_title(title.format(i) if title
                             else "index = {}".format(i))
                # ax.figure.canvas.draw()
                line.set_data(x, self[:, i])
                return line,

            anim = animation.FuncAnimation(
                fig, animate,
                frames=index,
                init_func=init,
                blit=False,  # if True, then cannot update `title/xlim/ylim`
                repeat=True,
                interval=interval,
                repeat_delay=1000,  # milliseconds
            )

            fig.canvas.mpl_connect('button_press_event',
                                   lambda event: _onclick(event, anim))
            plt.show()

            if output:
                if output.endswith('.gif'):
                    writer = 'imagemagick'
                    try:
                        animation.writers['imagemagick']
                    except KeyError:
                        raise ValueError(
                            "WARNING: save animation to gif not supported!\n"
                            "         try to intstall ImageMagick by:\n"
                            "     $ conda install -c kalefranz imagemagick!")
                else:
                    print("WARNING: the movie in this format may not work "
                          "         perfectly. '.gif' format is recommended!")
                    writer = 'ffmpeg'

                anim.save(output, writer=writer, fps=fps,
                          metadata=metadata, bitrate=bitrate)

            return anim

    def contourf(self, *args, **kwargs):
        """Plot (animated) contour/contourf/surface plot for 2D/3D data.

        Parameters
        ----------
        kind: str, optional, default: 'surface'

            - ['c', 'contour', 1, 'cf', 'contourf', 2]: contour/contourf plot
            - 'surface': 3D-surface plot

        newfig: bool, optional, default: True
            if Ture[default], create new figure,
            otherwise, plot on current figure and axes
        x/y: 1D array_like, optional, default: None
            the size should be same as data in x/y direction.
        x/y/zlabel: str, optional, default: None
            labels for x/y/z-axis,
        zleft: bool, optional, default: True
            draw z-axis at left side
        x/ylim: 2-elements data, optional, default: None
            axis limit for x/y-axis
            if None, auto-set to its index: [0, 1, ..., x/ysize-1]
        zlim: 2-elements data, optional, default: None
            axis limit for z-axis
            if None, auto-set to [`vmin`, `vmax`]
        vmin/vmax: number, optional, default: None
            set color limit to [`vmin`, `vmax`]
            if None, auto-set to the range of data
        title: str, optional, default: None
            figure title
            in animation, it is passed to 'title.format(frame_number)'
            or 'index = {}".format(frame_number) if it is None.
        cmap: Colormap, optional, default: plt.cm.bwr
            A cm Colormap instance.
        colorbar: bool, optional, default: True
            if True, plot colorbar
        cticks: 1D array_like, optional, default: None
            colorbar ticks.
            if None, auto-set to evenly spaced interval [`vmin`, `vmax`]
            by factor `ncticks`.
        ncticks: int, optional, default: 5
            the number of ticks of colorbar when `cticks` is not set.
        levels: 1D array_like, optional, default: None
            a list of floating point numbers indicating the level curves
            to draw, in increasing order.
            if None, auto-set to evenly spaced interval [`vmin`, `vmax`]
            by factor `nlevels`.
        nlevels: int, optional, default: 40
            the number of levels to contour/contourf draw.
        output: str, optional, default: None
            filename to store the figure or animation. It should include
            suffix. '.gif' format is recommended.

        **key-word arguments for 2D data**:
        index: int | array_like, default: 1

            - array_like: only using data[:, index] for animation.
            - int: only using data[:, ::index] for animation, the last
                frame is included as well.

        **key-word argments for animation**:
        interval: int, optional, default: 20
            delay between frames in milliseconds.
        fps: number, optional, default: 5
            frames per second in the movie.
        metadata: dict, optional, default: {artist:$USER}
            Dictionary of keys and values for metadata to include in the
            output file. Some keys that may be use include:
            title, artist, genre, subject, copyright, srcform, comment.
        bitrate: number, optional, default: -1
            Specifies the number of bits used per second in the compressed
            movie, in kilobits per second. A higher number means a higher
            quality movie, but at the cost of increased file size.
            -1 means let utility auto-determine.

        Returns
        -------
        ret: (figure object|animation object, colorbar object if exists)

        See Also
        --------
        :func:`matplotlib.pyplot.contour`
        :func:`matplotlib.pyplot.contourf`
        :meth:`mpl_toolkits.mplot3d.Axes3D.plot_surface`

        """

        # create new fig?
        newfig = kwargs.pop('newfig', True)
        if newfig:
            fig, ax = plt.subplots()
        else:
            fig = plt.gcf()
            ax = plt.gca()

        # auto squeeze array
        ndim = self.squeeze().ndim
        if ndim not in [2, 3]:
            raise ValueError("ERROR: only 2D/3D data supported.")
            return None
        xsize, ysize = self.squeeze().shape[:2]
        # xdata/ydata for x/y-axis
        x = kwargs.pop('x', None)
        y = kwargs.pop('y', None)
        if x is None:
            x = np.arange(xsize)
        if y is None:
            y = np.arange(ysize)

        # properties of fig
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        zlabel = kwargs.pop('zlabel', None)
        zleft = kwargs.pop('zleft', True)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        xlim = kwargs.pop('xlim', None)
        ylim = kwargs.pop('ylim', None)
        zlim = kwargs.pop('zlim', None)
        title = kwargs.pop('title', None)

        # colorbar
        # NOTE: if colorbar range is larger than data range,
        #       than explicit 'levels' should be set to show
        #       the full color range.
        colorbar = kwargs.pop('colorbar', True)
        cb = None   # colorbar object

        # set color limit
        vmin = kwargs.get('vmin', None)
        vmax = kwargs.get('vmax', None)
        if vmin is None:
            vmin = self.min()
        if vmax is None:
            vmax = self.max()
        if vmin == vmax:
            vmax += 1
        kwargs['vmin'], kwargs['vmax'] = vmin, vmax
        if zlim is None:
            zlim = [vmin, vmax]

        cticks = kwargs.pop('cticks', None)
        ncticks = kwargs.pop('ncticks', 5)
        if cticks is None:
            cticks = np.linspace(vmin, vmax, ncticks, endpoint=True)

        if 'cmap' not in kwargs:
            kwargs['cmap'] = plt.cm.bwr
        levels = kwargs.pop('levels', None)
        nlevels = kwargs.pop('nlevels', 40)
        # set number of contour color levels
        if levels is None:
            levels = np.linspace(vmin, vmax, nlevels, endpoint=True)

        # save fig/animation to as `output`
        output = kwargs.pop('output', None)

        # plot kinds: contour, contourf, surface
        kind = kwargs.pop('kind', 'surface')
        if kind in ['c', 'contour', 1]:
            kind = 'contour'
        elif kind in ['cf', 'contourf', 2]:
            kind = 'contourf'
        else:
            kind = 'surface'
        if kind == 'surface':
            ax.remove()
            ax = fig.add_subplot(111, projection='3d')
            # draw z-axis at left side
            # http://stackoverflow.com/questions/15042129/changing-position
            #   -of-vertical-z-axis-of-3d-plot-matplotlib/15048653#15048653
            if zleft:
                tmp_planes = ax.zaxis._PLANES
                ax.zaxis._PLANES = (tmp_planes[2], tmp_planes[3],
                                    tmp_planes[0], tmp_planes[1],
                                    tmp_planes[4], tmp_planes[5])
                view_1 = (25, -135)
                view_2 = (25, -45)
                init_view = view_1
                ax.view_init(*init_view)
                ax.tick_params(axis='z', pad=20)
                ax.zaxis.set_rotate_label(False)

            X, Y = np.meshgrid(y, x)

            if xlabel:
                ax.set_xlabel(xlabel, labelpad=25)
            if ylabel:
                ax.set_ylabel(ylabel, labelpad=25)
            if zlabel:
                ax.set_zlabel(zlabel, labelpad=45, rotation=90)
            if zlim:
                ax.set_zlim(zlim)

        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)
        if title:
            ax.set_title(title)

        # 2D data
        if ndim == 2:
            if kind in ['contour', 'contourf']:
                kwargs['levels'] = levels
            if kind == 'contour':
                ret = ax.contour(x, y, self.squeeze().T, *args, **kwargs)
                ret.set_clim(vmin, vmax)
            elif kind == 'contourf':
                ret = ax.contourf(x, y, self.squeeze().T, *args, **kwargs)
                ret.set_clim(vmin, vmax)
            else:
                ret = ax.plot_surface(X, Y, self.squeeze(), *args, **kwargs)

            if colorbar:
                cb = plt.colorbar(ret, ticks=cticks)

            plt.tight_layout()
            if cb:
                return ret, cb
            return ret

        # animation
        if ndim == 3:
            #  position the colorbar, it's easier to animate the colorbar
            #  div = make_axes_locatable(ax)
            #  cax = div.append_axes('right', '2%', '3%')
            #  plt.subplots_adjust(right=0.85)

            zsize = self.squeeze().shape[2]
            index = kwargs.pop('index', 1)
            if isinstance(index, int):
                index = range(0, zsize, index)
                # include last step
                if index[-1] != zsize - 1:
                    index.append(zsize - 1)

            # options for animation
            interval = kwargs.pop('interval', 20)
            fps = kwargs.pop('fps', 5)
            metadata = kwargs.pop('metadata', dict(artist=os.environ['USER']))
            bitrate = kwargs.pop('bitrate', -1)

            # initialization function: plot the background of each frame
            def init():
                ax.cla()
                if xlabel:
                    ax.set_xlabel(xlabel)
                return

            # animation function: This is called sequentially
            def animate(i):
                # update plot
                ax.cla()
                if zlim and kind == 'surface':
                    ax.set_zlim(zlim)
                # set_title by 'position' to avoid change in animation
                ax.set_title(title.format(i) if title
                             else "index = {}".format(i),
                             position=(0.5, 1.05), transform=ax.transAxes,
                             horizontalalignment='center')
                if xlabel:
                    ax.set_xlabel(xlabel)
                if ylabel:
                    ax.set_ylabel(ylabel)
                if zlabel:
                    ax.set_zlabel(zlabel)
                # ax.figure.canvas.draw()
                if kind == 'contour':
                    ret = ax.contour(x, y, self[:, :, i].squeeze().T,
                                     *args, **kwargs)
                elif kind == 'contourf':
                    ret = ax.contourf(x, y, self[:, :, i].squeeze().T,
                                      *args, **kwargs)
                else:
                    ret = ax.plot_surface(X, Y, self[:, :, i].squeeze(),
                                          *args, **kwargs)
                return ret

            if colorbar and kind != 'surface':
                kwargs['levels'] = levels
                ret = animate(index[0])
                cb = fig.colorbar(ret, ticks=cticks)

            anim = animation.FuncAnimation(
                fig, animate,
                frames=index,
                init_func=init,
                blit=False,  # if True, then cannot update `title/xlim/ylim`
                repeat=True,
                interval=interval,
                repeat_delay=1000,  # milliseconds
            )

            fig.canvas.mpl_connect('button_press_event',
                                   lambda event: _onclick(event, anim))
            plt.show()

            if output:
                if output.endswith('.gif'):
                    writer = 'imagemagick'
                    try:
                        animation.writers['imagemagick']
                    except KeyError:
                        raise ValueError(
                            "WARNING: save animation to gif not supported!\n"
                            "         try to intstall ImageMagick by:\n"
                            "     $ conda install -c kalefranz imagemagick!")
                else:
                    writer = 'ffmpeg'

                anim.save(output, writer=writer, fps=fps,
                          metadata=metadata, bitrate=bitrate)

            if cb:
                return anim, cb
            return anim

    def showdata(self, *args, **kwargs):
        """Visualisation and animation for 1-3D data.

        This function is just a wrapper function for **plot** and **contourf**.
        All **args** and **kwargs** are passed to these functions according to
        the dimension of data and key 'kind'.

        Parameters
        ----------
        kind: str
            plot type. the value for different dimension of data:

            - 1D-data:
                None: plot single line
            - 2D-data:

                - 'surface': surface plot [default]
                - 'c', 'contour', 1, 'cf', 'contourf', 2:
                    contour/contourf plot
                - 'm', 'multi', 'multilines': multi-lines in one figure
                - 'animation': animated lines

            - 3D-data:
                'c', 'contour', 1; 'cf', 'contourf', 2; 'surface':
                    animated contour/contourf/surface plot

        Other parameters:
            check function :meth:`~boutpy.boutdata.Field.plot` and
            :meth:`boutpy.boutdata.Field.contourf` for details

        See Also
        --------
        :meth:`boutpy.boutdata.Field.plot`:
            plot 1D data and 2D data(multilines or animation).
        :meth:`boutpy.boutdata.Field.contourf`:
            plot 2D data and 3D data(contourf/surface or animation)

        """

        # auto squeeze array
        ndim = self.squeeze().ndim
        if ndim not in [1, 2, 3]:
            raise ValueError("ERROR: only 1,2,3-D data supported.")
            return None

        if ndim == 1:
            return self.plot(*args, **kwargs)
        elif ndim == 2:
            if 'kind' not in kwargs:
                kwargs['kind'] = 'surface'
            if kwargs['kind'] in ['m', 'multi', 'multilines', 'animation']:
                return self.plot(*args, **kwargs)
            else:
                return self.contourf(*args, **kwargs)
        else:
            return self.contourf(*args, **kwargs)
