from networkx.drawing.nx_pydot import to_pydot


def draw(nx_graph, color=None, fillcolor=None, observed_fillcolor=None, highlight_color=None,
         highlight_observed_fillcolor=None, encoding=None):
    color = color or '#808080'
    fillcolor = fillcolor or '#FFFFFF'
    observed_fillcolor = observed_fillcolor or '#F0F0F0'
    highlight_color = highlight_color or '#76B900'
    highlight_observed_fillcolor = highlight_observed_fillcolor or '#DCEDC8'
    encoding = encoding or 'utf-8'

    keep_pos = False

    for s in nx_graph.nodes:
        node = nx_graph.nodes[s]

        if 'pos' in node:
            keep_pos = True

            if not isinstance(node['pos'], str):
                node['pos'] = '"{},{}"'.format(node['pos'][0], node['pos'][1])

        node['style'] = 'filled'
        node['color'] = color
        node['fillcolor'] = fillcolor

        if node.get('observed'):
            node['fillcolor'] = observed_fillcolor

        if node.get('highlight'):
            node['color'] = highlight_color

            if node.get('observed'):
                node['fillcolor'] = highlight_observed_fillcolor

    for t in nx_graph.edges:
        edge = nx_graph.edges[t]
        edge['color'] = color

        if edge.get('highlight'):
            edge['color'] = highlight_color

    prog = ['neato', '-n2'] if keep_pos else 'dot'
    return to_pydot(nx_graph).create_svg(prog=prog).decode(encoding)


def reset_highlighting(nx_graph):
    for e in nx_graph.edges:
        nx_graph.edges[e]['highlight'] = False
    for n in nx_graph.nodes:
        nx_graph.nodes[n]['highlight'] = False


def highlight_path(nx_graph, path, reset=False):
    if reset:
        reset_highlighting(nx_graph)

    if len(path) == 0:
        return

    if len(path) == 1:
        nx_graph.nodes[path[0]]['highlight'] = True
        return

    for n1, n2 in zip(path[:-1], path[1:]):
        nx_graph.nodes[n1]['highlight'] = True
        nx_graph.nodes[n2]['highlight'] = True

        if (n1, n2) in nx_graph.edges:
            nx_graph.edges[(n1, n2)]['highlight'] = True

        if (n2, n1) in nx_graph.edges:
            nx_graph.edges[(n2, n1)]['highlight'] = True
