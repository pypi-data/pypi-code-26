from .cary5000_data_reader import  Cary5000DataReader
from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import numpy as np


class Cary5000:

    def __init__(self, filename):
        self.filename = filename
        self.data = Cary5000DataReader.read_data(filename=self.filename)

    def get_wavelength(self, sample):
        return self.data[sample].wavelength

    def get_transmission(self, sample):
        return self.data[sample].transmission

    def get_samples(self):
        return self.data.keys()

    def plotly_all(self, title='', mode='transmission'):
        init_notebook_mode(connected=True)
        data = []
        for sample in self.get_samples():
            if sample == 'Baseline':
                continue
            x = self.data[sample].wavelength
            y = self.data[sample].transmission
            if mode=='Arturo':
                trace = Cary5000._create_x_y_trace(x, 100-y, sample)
            else:
                trace = Cary5000._create_x_y_trace(x, y, sample)
            data.append(trace)
        layout = Cary5000._get_plotly_layout(title, mode=mode)
        fig = go.Figure(data=data, layout=layout)
        return iplot(fig)

    def plot_sample(self,sample,ax=None, label=None):
        if ax is None:
            ax = plt.axes()
        if label is None:
            ax.plot(self.get_wavelength(sample),self.get_transmission(sample),label=sample)
        else:
            ax.plot(self.get_wavelength(sample),self.get_transmission(sample),label=label)
        return ax

    def find_peak(self,sample):
        transmission = self.get_transmission(sample)
        wavelength = self.get_wavelength(sample)
        index_of_min = np.argmin(transmission)
        return wavelength[index_of_min], transmission[index_of_min], index_of_min


    @staticmethod
    def _create_x_y_trace(x, y, name):
        if name == 'Baseline 100%T':
            return go.Scatter(x=x, y=y, name=name, visible='legendonly')
        else:
            return go.Scatter(x=x, y=y, name=name)

    @staticmethod
    def _get_plotly_layout(title='', mode='transmission'):
        if mode=='transmission':
            return go.Layout(
                title = title,
                xaxis=dict(
                    title='Wavelength [nm]'
                ),
                yaxis=dict(
                    title='%T'
                )
            )
        else:
            return go.Layout(
                title=title,
                xaxis=dict(
                    title='Wavelength [nm]'
                ),
                yaxis=dict(
                    title='extinction'
                )
            )

