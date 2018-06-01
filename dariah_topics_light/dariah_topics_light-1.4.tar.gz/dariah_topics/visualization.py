import logging
import numpy as np
import os
import pandas as pd
from bokeh.plotting import figure
from bokeh import palettes
from bokeh.models import (
            ColumnDataSource,
            HoverTool,
            LinearColorMapper,
            BasicTicker,
            ColorBar
            )
from collections import Counter


log = logging.getLogger(__name__)


class PlotDocumentTopics:
    """
    Class to visualize document-topic matrix.
    """
    def __init__(self, document_topics):
        self.document_topics = document_topics

    def interactive_heatmap(self, palette=palettes.Blues[9], reverse_palette=True,
                            tools='hover, pan, reset, save, wheel_zoom, zoom_in, zoom_out',
                            width=1000, height=550, x_axis_location='below', toolbar_location='above',
                            sizing_mode='fixed', line_color=None, grid_line_color=None, axis_line_color=None,
                            major_tick_line_color=None, major_label_text_font_size='9pt',
                            major_label_standoff=0, major_label_orientation=3.14/3, colorbar=True):
        """Plots an interactive heatmap.
    
        Args:
            palette (list), optional: A list of color values. Defaults to ``palettes.Blues[9]``.
            reverse_palette (bool), optional: If True, color values of ``palette`` will
                be reversed. Defaults to True.
            tools (str), optional: Tools, which will be includeded. Defaults to ``hover,
                pan, reset, save, wheel_zoom, zoom_in, zoom_out``.
            width (int), optional: Width of the figure. Defaults to 1000.
            height (int), optional: Height of the figure. Defaults to 550.
            x_axis_location (str), optional: Location of the x-axis. Defaults to
                ``below``.
            toolbar_location (str), optional: Location of the toolbar. Defaults to
                ``above``.
            sizing_mode (str), optional: Size fixed or width oriented. Defaults to ``fixed``.
            line_color (str): Color for lines. Defaults to None.
            grid_line_color (str): Color for grid lines. Defaults to None.
            axis_line_color (str): Color for axis lines. Defaults to None.
            major_tick_line_color (str): Color for major tick lines. Defaults to None.
            major_label_text_font_size (str): Font size for major label text. Defaults
                to ``9pt``.
            major_label_standoff (int): Standoff for major labels. Defaults to 0.
            major_label_orientation (float): Orientation for major labels. Defaults
                to ``3.14 / 3``.
            colorbar (bool): If True, colorbar will be included.

        Returns:
            Figure object.
        """        
        if reverse_palette:
            palette = list(reversed(palette))

        x_range = list(self.document_topics.columns)
        y_range = list(self.document_topics.index)
        
        stacked_data = pd.DataFrame(self.document_topics.stack()).reset_index()
        stacked_data.columns = ['Topics', 'Documents', 'Distributions']
        mapper = LinearColorMapper(palette=palette,
                                   low=stacked_data.Distributions.min(),
                                   high=stacked_data.Distributions.max())
        source = ColumnDataSource(stacked_data)
        
        fig = figure(x_range=x_range,
                     y_range=y_range,
                     x_axis_location=x_axis_location,
                     plot_width=width, plot_height=height,
                     tools=tools, toolbar_location=toolbar_location,
                     sizing_mode=sizing_mode,
                     logo=None)
        fig.rect(x='Documents', y='Topics', source=source, width=1, height=1,
                 fill_color={'field': 'Distributions', 'transform': mapper},
                 line_color=line_color)

        fig.grid.grid_line_color = grid_line_color
        fig.axis.axis_line_color = axis_line_color
        fig.axis.major_tick_line_color = major_tick_line_color
        fig.axis.major_label_text_font_size = major_label_text_font_size
        fig.axis.major_label_standoff = major_label_standoff
        fig.xaxis.major_label_orientation = major_label_orientation
        
        if 'hover' in tools:
            fig.select_one(HoverTool).tooltips = [('x-Axis', '@Documents'),
                                                  ('y-Axis', '@Topics'),
                                                  ('Score', '@Distributions')]

        if colorbar:
            feature = ColorBar(color_mapper=mapper, major_label_text_font_size=major_label_text_font_size,
                               ticker=BasicTicker(desired_num_ticks=len(palette)),
                               label_standoff=6, border_line_color=None, location=(0, 0))
            fig.add_layout(feature, 'right')
        return fig
