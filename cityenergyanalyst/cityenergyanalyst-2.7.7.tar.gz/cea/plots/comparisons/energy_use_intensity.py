from __future__ import division
from __future__ import print_function

import plotly.graph_objs as go
from plotly.offline import plot

from cea.plots.variable_naming import NAMING, LOGO, COLOR


def energy_use_intensity(data_frame, analysis_fields, title, output_path):
    # CALCULATE GRAPH
    traces_graph = calc_graph(analysis_fields, data_frame)

    # CALCULATE TABLE
    traces_table = calc_table(analysis_fields, data_frame)

    # PLOT GRAPH
    traces_graph.append(traces_table)
    layout = go.Layout(images=LOGO, title=title, barmode='stack',
                       yaxis=dict(title='Energy Use Intensity [kWh/m2.yr]', domain=[0.35, 1]),
                       xaxis=dict(title='Scenario Name'))
    fig = go.Figure(data=traces_graph, layout=layout)
    plot(fig, auto_open=False, filename=output_path)

    return {'data': traces_graph, 'layout': layout}


def calc_graph(analysis_fields, data_frame):
    # calculate graph
    graph = []
    for field in analysis_fields:
        data_frame[field] = data_frame[field] * 1000 / data_frame["GFA_m2"]  # in kWh/m2y
    data_frame['total'] = total = data_frame[analysis_fields].sum(axis=1)
    data_frame = data_frame.sort_values(by='total', ascending=False)  # this will get the maximum value to the left
    for field in analysis_fields:
        y = data_frame[field]
        total_perc = (y / total * 100).round(2).values
        total_perc_txt = ["(" + str(x) + " %)" for x in total_perc]
        name = NAMING[field]
        trace = go.Bar(x=data_frame.index, y=y, name=name, text=total_perc_txt, orientation='v',
                       marker=dict(color=COLOR[field]))
        graph.append(trace)

    return graph

def calc_table(analysis_fields, data_frame):

    #create values of table
    values_header = ['Scenarios']
    for field in analysis_fields+['total']:
        values_header.append("delta " + field + "[kWh/m2.yr]")

    #create values of table
    values_cell = [data_frame.index]
    for field in analysis_fields+['total']:
        cell = data_frame[field]
        cell = [
            str('{:20,.2f}'.format(x - cell[0])) + " (" + str(
                round((x - cell[0]) / cell[0] * 100, 1)) + " %)"
            for x in cell]
        values_cell.append(cell)

    table = go.Table(domain=dict(x=[0, 1], y=[0.0, 0.2]),
                     header=dict(values=values_header),
                     cells=dict(values=values_cell))
    return table
