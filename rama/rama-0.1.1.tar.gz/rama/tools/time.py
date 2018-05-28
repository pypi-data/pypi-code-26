# Copyright 2018 Smithsonian Astrophysical Observatory
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
# disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from astropy.visualization import quantity_support
quantity_support()

from rama.adapters.cube import TimeAxis


class TimeSeries:
    def __init__(self, cube_object):
        self.time = None
        self.dependent = []
        self._index = {}

        for axis in cube_object.axes:
            if not axis.dependent and isinstance(axis, TimeAxis):
                self.time = axis
                self._index['time'] = axis
            elif axis.dependent:
                self.dependent.append(axis)
                self._index[axis.name] = axis

        if self.time is None:
            raise AttributeError("This is not a time series, there is no independent axis for Time")

    def __getitem__(self, item):
        return self._index[item]


def plot(ax, cube_object, **kwargs):
    time_series = TimeSeries(cube_object)

    kwargs['fmt'] = '.'

    time = PlottableAxis(time_series.time)
    if time.error is not None:
        kwargs['xerr'] = time.error

    ax.set_prop_cycle('color', ['#984ea3', '#4daf4a', '#377eb8', '#ff7f00', '#dede00', '#f781bf', '#a65628',
                                '#999999', '#e41a1c'])
    ax.set_xlabel(time.label)
    ax.set_title("Time Series")

    plots = []
    labels = []

    for idx, axis in enumerate(time_series.dependent):
        if idx > 0:
            plot_ax = ax.twinx()
            plot_ax._get_lines.prop_cycler = ax._get_lines.prop_cycler
        else:
            plot_ax = ax

        local_args = dict(kwargs)

        if not axis.is_scalar:
            dependent = PlottableAxis(axis)

            # try:
            plot = plot_ax.errorbar(time.value, dependent.value, **local_args, yerr=dependent.error)
            # except UnitsError:
            #     plot = plot_ax.errorbar(time.value, dependent.value, **local_args)

            plot_ax.set_ylabel(dependent.label)
            labels.append(dependent.label)

            plots.append(plot)

    ax.legend(plots, labels, loc=0)
    print(plots, labels)


class PlottableAxis:
    def __init__(self, axis):
        self._axis = axis

    @property
    def value(self):
        return self._axis.measurement

    @property
    def error(self):
        try:
            # FIXME implement the correct objects for each 1D error type
            err = self._axis.stat_error.radius
        except AttributeError:
            err = None

        return err

    @property
    def label(self):
        label = self._axis.name
        if hasattr(self._axis, 'unit'):
            label += f" ({self._axis.unit})"
        return label