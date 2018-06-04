from FEV_KEGG.Graph import Models
import networkx.classes
import os
from enum import Enum

LABEL_NAME = 'custom_label'
"""
Name of the column of the graph to be used for storing the label.
"""
COLOUR_NAME = 'colour'
"""
Name of the column of the graph to be used for storing the colour.
"""

def addLabelAttribute(nxGraph: networkx.classes.MultiGraph):
    """
    Adds the "custom_label" column to each node and edge.
    
    Add an attribute to nodes and edges called "custom_label" (see module variable :attr:`LABEL_NAME`) containing the string of the node's id, or the edge's key, repectively.
    This is especially useful if the tool you import this file into does not regularly read the id parameter. For example, Cytoscape does not for edges.
    
    Parameters
    ----------
    nxGraph : networkx.classes.MultiGraph
        A NetworkX graph object.
    """
    if not isinstance(nxGraph, networkx.classes.graph.Graph):
        raise NotImplementedError()
    
    # add label to edges
    edges = nxGraph.edges(keys = True)

    attributeDict = dict()
    for edge in edges:
        attributeDict[edge] = edge[2].__str__()
    
    networkx.set_edge_attributes(nxGraph, attributeDict, LABEL_NAME)
    
    # add label to nodes
    nodes = nxGraph.nodes
    
    attributeDict = dict()
    for node in nodes:
        attributeDict[node] = node.__str__()
    
    networkx.set_node_attributes(nxGraph, attributeDict, LABEL_NAME)


class Colour(Enum):
    BLUE = '#4444FF'
    RED = '#FF5555'
    PINK = '#FF66FF'
    GREEN = '#55FF55'
    YELLOW = '#FFFF55'
    TURQUOISE = '#55FFFF'

def addColourAttribute(graph: Models.CommonGraphApi, colour : Colour, nodes = False, edges = False):
    """
    Adds the "colour" column to selected nodes/edges.
    
    If both, `nodes` and `edges` are *False*, nothing is coloured.
    Adds an attribute to nodes and edges called "colour" (see module variable :attr:`COLOUR_NAME`) containing the string of a hex value of a colour in RGB, see :class:`Colour`.
    
    Parameters
    ----------
    graph : Models.CommonGraphApi
        A NetworkX graph object.
    colour : Colour
        Colour to use.
    nodes : Iterable[NodeView] or bool, optional
        Nodes to be coloured, i.e. annotated with the "colour" column containing `colour`. If *True*, all nodes are coloured.
    edges : Iterable[EdgeView] or bool, optional
        Edges to be coloured, i.e. annotated with the "colour" column containing `colour`. If *True*, all edges are coloured.
    
    Warnings
    ----
    Any operation on the resulting graph, e.g. :func:`FEV_KEGG.Graph.Models.CommonGraphApi.intersection`, removes the colouring. It actually removes all attributes.
    """
    nxGraph = graph.underlyingRawGraph
    if not isinstance(nxGraph, networkx.classes.graph.Graph):
        raise NotImplementedError("This graph model can not be coloured, yet.")
    
    # add color to edges
    if edges is not False:
        # colour something
        if edges is True:
            # colour everything
            edgesToColour = nxGraph.edges
        else:
            # colour what is in `edges`
            edgesToColour = edges
        
        attributeDict = dict()
        for edge in edgesToColour:
            attributeDict[edge] = colour.value
        
        networkx.set_edge_attributes(nxGraph, attributeDict, COLOUR_NAME)
    
    # add color to nodes
    if nodes is not False:
        # colour something
        if nodes is True:
            # colour everything
            nodesToColour = nxGraph.nodes
        else:
            # colour what is in `nodes`
            nodesToColour = nodes
        
        attributeDict = dict()
        for node in nodesToColour:
            attributeDict[node] = colour.value
        
        networkx.set_node_attributes(nxGraph, attributeDict, COLOUR_NAME)


def toGraphML(graph: Models.CommonGraphApi, file):
    """
    Export `graph` to `file` in GraphML format.
    
    Parameters
    ----------
    graph : Models.CommonGraphApi
        The graph to be exported.
    file : str
        Path and name of the exported file. This path is relative to the current working directory!
        
    Raises
    ------
    NotImplementedError
        If `graph` is not of a NetworkX type.
    """
    nxGraph = graph.underlyingRawGraph
    if isinstance(nxGraph, networkx.classes.graph.Graph):
        
        dirName = os.path.dirname(file)
        if not os.path.isdir(dirName) and dirName != '':
            os.makedirs(os.path.dirname(file))
        
        networkx.write_graphml_xml(nxGraph, file + '.graphml', prettyprint=False)
        
    else:
        raise NotImplementedError()


def toGML(graph: Models.CommonGraphApi, file):
    """
    Export `graph` to `file` in GML format.
    
    Parameters
    ----------
    graph : Models.CommonGraphApi
        The graph to be exported.
    file : str
        Path and name of the exported file. This path is relative to the current working directory!
     
    Raises
    ------
    NotImplementedError
        If `graph` is not of a NetworkX type.
    """
    nxGraph = graph.underlyingRawGraph
    if isinstance(nxGraph, networkx.classes.graph.Graph):
            
        dirName = os.path.dirname(file)
        if not os.path.isdir(dirName) and dirName != '':
            os.makedirs(os.path.dirname(file))
        
        networkx.write_gml(nxGraph, file + '.gml', lambda x: x.__str__())
        
    else:
        raise NotImplementedError()
    
def forCytoscape(graph: Models.CommonGraphApi, file):
    """
    Export `graph` to `file` in GraphML format, including some tweaks for Cytoscape.
    
    Parameters
    ----------
    graph : Models.CommonGraphApi
        The graph to be exported.
    file : str
        Path and name of the exported file. This path is relative to the current working directory!
            
    Raises
    ------
    NotImplementedError
        If `graph` is not of a NetworkX type.
    """
    addLabelAttribute(graph.underlyingRawGraph)    
    toGraphML(graph, file)
    