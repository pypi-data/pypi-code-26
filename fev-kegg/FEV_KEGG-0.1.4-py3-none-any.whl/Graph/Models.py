from math import ceil

import networkx.algorithms.components
import networkx.algorithms.operators.all
from typing import Set, Tuple, Generator, Iterable

from FEV_KEGG.Graph import Elements
from FEV_KEGG.Graph.Implementations.NetworkX import NetworkX, MultiDiGraph, MultiGraph


class CommonGraphApi(object):
    # choose a lib as implementation of graphs
    implementationLib = NetworkX
    """
    Implementation library of a general graph. This implementation should be able to differentiate between directed and undirected graphs, see :attr:`DirectedMultiGraph.implementationGraph` and :attr:`UndirectedMultiGraph.implementationGraph`
    """
    
    def __init__(self, underlyingRawGraph = None):
        """
        Represents any type of graph.
        
        The library to implement graphs is chosen here.
        
        Parameters
        ----------
        underlyingRawGraph : :attr:`implementationLib`, optional
            If not *None*, copies `underlyingRawGraph` and stores it for this object.
        
        Attributes
        ----------
        self.underlyingRawGraph : :mod:`FEV_KEGG.Graph.Implementations`
            The actual graph containing the data. This is dependant on the implementation chosen in :attr:`implementationLib`.
        self.name : str
            Custom name of the graph. This is often set, but not necessary in any calculations.
        self.nodeCounts : Dict[Element, int], optional
            Number of precursor graphs which contained certain :class:`Element` nodes still in this graph. *None* by default.
        self.edgeCounts : Dict[Tuple[Element, Element, Element], int], optional
            Number of precursor graphs which contained a certain edge (a Tuple of three :class:`Element`) still in this graph. *None* by default.
        self.edgeElementCounts : Dict[Element, int], optional
            Number of precursor graphs which contained certain :class:`Element` edge keys still in this graph. *None* by default.
        """
        if underlyingRawGraph != None:
            self.underlyingRawGraph = underlyingRawGraph.copy()
        
        self.nodeCounts = None
        self.edgeCounts = None
        self.edgeElementCounts = None
    
    @property
    def name(self):
        """
        Custom name of the graph.
        
        This is often set in calcuations, but not used for any calculations.
        
        Returns
        -------
        str
            Custom name of the graph.
        """
        return self.underlyingRawGraph.name
    @name.setter
    def name(self, name: str):
        self.underlyingRawGraph.name = name
        
    @classmethod
    def composeAll(cls, graphs: Iterable['CommonGraphApi'], name: str = None, pathwaySet = None) -> 'CommonGraphApi':
        """
        Simple UNION of node and edge lists.
        
        A node is defined by its hash(). An edge is defined by Tuple[node1, node2, hash(edge key)], while the order of node1 and node2 encodes the direction, if the graph is directed.
        This is similar to :func:`union`, but aims at a special use case. You will most likely want to use :func:`union`.
        
        Parameters
        ----------
        graphs : Iterable[CommonGraphApi]
            Iterable of graphs to be composed.
        name : str, optional
            Name of the new graph.
        pathwaySet : Set[KGML_pathway.Pathway], optional
            Set of pathways this graph was derived from. Especially useful for e.g. :func:`FEV_KEGG.Graph.SubstrateGraphs.Conversion.SubstrateReactionGraph2SubstrateGeneGraph`.
        
        Returns
        -------
        CommonGraphApi
            Composition of all `graphs` by simple union operation. Includes `pathwaySet`, if given.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        # for all implementations
        allUnderlyingGraphs = []
        
        for abstractGraph in graphs:
            underlyingGraph = abstractGraph.underlyingRawGraph
            allUnderlyingGraphs.append(underlyingGraph)
            
        # NetworkX was chosen as graph implementation
        if cls.implementationLib == NetworkX:
            
            newUnderlyingGraph = networkx.algorithms.operators.all.compose_all(allUnderlyingGraphs)
            newGraph = cls()
            newGraph.underlyingRawGraph = newUnderlyingGraph
            if name is not None:
                newGraph.name = name
            
            if pathwaySet is not None: # some graph had a set of pathways it was derived from, apply it to the new graph
                newGraph.pathwaySet = pathwaySet
            
            return newGraph
        
        # unknown implementation
        else:
            raise NotImplementedError
        
    def getNodes(self) -> Set[Elements.Element]:
        """
        Get all nodes.
        
        Returns
        -------
        Set[Element]
            A set-like object of all nodes. Even though the type list does not enforce it, this should never return duplicates.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            return self.underlyingRawGraph.nodes
            
        # unknown implementation
        else:
            raise NotImplementedError
        
    def getEdges(self) -> Set[Tuple]:
        """
        Get all edges.
        
        Returns
        -------
        Set[Tuple[Element, Element, Element]]
            A set-like object of all edges, defined by Tuples of (node1, node2, edge key).
            This is **not** a copy, but the original internal list. Do **not** change while iterating! Make a copy instead: copy = list(getEdges())
            Only returns outgoing edges, so that no edge is reported twice.
            Even though the type list does not enforce it, this should never return duplicates.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationGraph == MultiDiGraph:
            
            return self.underlyingRawGraph.edges(keys=True)
        
        # unknown implementation
        else:
            raise NotImplementedError
    
    def addNode(self, node: Elements.Element):
        """
        Add a node to the graph.
        
        Parameters
        ----------
        node : Element
            Node to add to the graph, if not already present.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationGraph`.
        """
        
        # NetworkX.MultiDiGraph was chosen as graph implementation
        if self.__class__.implementationGraph == MultiDiGraph:

            self.underlyingRawGraph.add_node(node)
                
        # unknown implementation
        else:
            raise NotImplementedError
    
    def addNodes(self, nodes: Iterable[Elements.Element]):
        """
        Add nodes to the graph.
        
        Parameters
        ----------
        nodes : Iterable[Element]
            Iterable of elements to be added as nodes.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            self.underlyingRawGraph.add_nodes_from(nodes)
            
        # unknown implementation
        else:
            raise NotImplementedError
    
    def addEdge(self, node1: Elements.Element, node2: Elements.Element, key: Elements.Element, isReversible: bool = False):
        """
        Add an edge to the graph.
        
        Parameters
        ----------
        node1 : Element
            Node from which the newly created edge starts. Is added to the graph, if not already present.
        node2 : Element
            Node at which the newly created edge ends. Is added to the graph, if not already present.
        key : Element
            Edge key element annotating the newly created edge.
        isReversible : bool, optional
            If *True*, both directions are added, swapping `node1` and `node2`. If the graph is undirected, this option is ignored.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationGraph`.
        """
        
        # NetworkX.MultiDiGraph was chosen as graph implementation
        if self.__class__.implementationGraph == MultiDiGraph:

            self.underlyingRawGraph.add_edge(node1, node2, key) # automatically creates node, if not already present
            if isReversible == True:
                self.underlyingRawGraph.add_edge(node2, node1, key) # also add reverse direction
                
        # unknown implementation
        else:
            raise NotImplementedError
    
    def addEdges(self, edges: Iterable[Tuple[Elements.Element, Elements.Element, Elements.Element]]):
        """
        Add edges to the graph.
        
        Parameters
        ----------
        edges : Iterable[Tuple[Element, Element, Element]]
            Iterable of edge tuples, defined as (node1, node2, edge key). If the nodes do not already exist, they are silently added. If the graph is directed, the order of node1 and node2 counts as direction.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            self.underlyingRawGraph.add_edges_from(edges)
            
        # unknown implementation
        else:
            raise NotImplementedError
        
    def removeEdge(self, node1: Elements.Element, node2: Elements.Element, key:Elements.Element, bothDirections: bool = False):
        """
        Remove an edge from the graph.
        
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Parameters
        ----------
        node1 : Element
            Node from which the edge to be removed starts. Is not removed itself.
        node2 : Element
            Node at which the edge to be removed ends. Is not removed itself.
        key : Element
            Edge key element annotating the edge to be removed.
        bothDirections : bool, optional
            If *True*, both directions are removed, swapping `node1` and `node2`. If the graph is undirected, this option is ignored.        
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationGraph`.
        """
        # NetworkX.MultiDiGraph was chosen as graph implementation
        if self.__class__.implementationGraph == MultiDiGraph:
            
            self.underlyingRawGraph.remove_edge(node1, node2, key)
            if bothDirections == True:
                self.underlyingRawGraph.remove_edge(node2, node1, key) # also add reverse direction
                
        # unknown implementation
        else:
            raise NotImplementedError
    
    def removeEdges(self, edges: Iterable[Tuple[Elements.Element, Elements.Element, Elements.Element]]):
        """
        Remove certain `edges`.
        
        Parameters
        ----------
        edges : Iterable[Tuple[Element, Element, Element]]
            Iterable of edge tuples for edges to be removed, defined as (node1, node2, edge key). If an edge to be removed does not exist, the next edge will be tried, without any error message.
            If the graph is directed, the order of node1 and node2 counts as direction. The edge of opposing direction is not removed.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            self.underlyingRawGraph.remove_edges_from(edges)
            
        # unknown implementation
        else:
            raise NotImplementedError
    
    def removeEdgesByElement(self, elements: Iterable[Elements.Element]):
        """
        Removes all edges associated with each an :class:`Element` in `elements`.
        
        Parameters
        ----------
        elements : Iterable[Element]
            Iterable of edge keys. Every edge keyed with an edge key equal (by __eq__) to any of these `elements` is removed.
            Direction of the graph does not affect removal.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        # NetworkX.MultiDiGraph was chosen as graph implementation
        if self.__class__.implementationGraph == MultiDiGraph:
            
            allEdges = self.getEdges()
            
            edgesToBeRemoved = []
            
            for edgeTuple in allEdges:
                _, _, element = edgeTuple
                
                if element in elements:
                    edgesToBeRemoved.append(edgeTuple)
            
            self.removeEdges(edgesToBeRemoved)
                
        # unknown implementation
        else:
            raise NotImplementedError
    
    def getIsolatedNodes(self) -> Iterable[Elements.Element]:
        """
        Get all nodes without any edge to another node.
        
        Returns
        -------
        Iterable[Element]
            Iterable of nodes without any edge to another node. Even though the type does not enforce it, this should never return duplicates.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            return list(networkx.algorithms.isolate.isolates(self.underlyingRawGraph))
            
        # unknown implementation
        else:
            raise NotImplementedError
    
    def removeNodes(self, nodes: Iterable[Elements.Element]):
        """
        Remove all `nodes`.
        
        Parameters
        ----------
        nodes : Iterable[Element]
            Iterable of elements representing nodes to be removed. Any edges involving these nodes are removed as well!
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            self.underlyingRawGraph.remove_nodes_from(nodes)
            
        # unknown implementation
        else:
            raise NotImplementedError
    
    def removeIsolatedNodes(self):
        """
        Remove all nodes without any edge to another node.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        self.removeNodes(self.getIsolatedNodes())
        
        return self
        
    def removeSmallComponents(self, upToNumberOfNodes: int):
        """
        Remove every isolated component of the graph with a total count of nodes <= `upToNumberOfNodes`.
        
        For a directed graph, this considers weakly connected components, too. This means that there do **not** have to be edges in **both** directions to be counted as a component.
        Even an edge in only one direction counts as connecting a component.
        
        Parameters
        ----------
        upToNumberOfNodes : int
            Maximum number of nodes a component has to connect to be completely removed.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        components = self.getComponents()
        
        nodesToRemove = []
        
        for componentNodes in components:
            if len( componentNodes ) <= upToNumberOfNodes: # component too small
                nodesToRemove.extend(componentNodes)
        
        # remove this component completely
        self.removeNodes(nodesToRemove)
        
        return self
    
    def getComponents(self) -> Generator[Set, None, None]:
        """
        Get all isolated components.
        
        For a directed graph, this considers weakly connected components, too. This means that there do **not** have to be edges in **both** directions to be counted as a component.
        Even an edge in only one direction counts as connecting a component.
        
        Returns
        -------
        Generator[Set[Element]]
            Generator of any isolated component of the graph. Each represented by a set of their nodes, each represented by an Element.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            if isinstance(self, UndirectedMultiGraph): # undirected graph
                return networkx.algorithms.components.connected_components(self.underlyingRawGraph)
            
            elif isinstance(self, DirectedMultiGraph): # directed graph
                return networkx.algorithms.components.weakly_connected_components(self.underlyingRawGraph)
            
        # unknown implementation
        else:
            raise NotImplementedError
    
    def getLargestComponent(self) -> Set[Elements.Element]:
        """
        Get largest component.
        
        Returns
        -------
        Set[Element]
            Set of all nodes, represented by an Element, of the largest component.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        return max(self.getComponents(), key=len)
    
    def getSubgraph(self, byNodes:Iterable[Elements.Element] = None, byEdges:Iterable[Tuple[Elements.Element, Elements.Element, Elements.Element]] = None) -> 'CommonGraphApi':
        """
        Get sub-graph defined by nodes or edges.
        
        If both are passed, only nodes are used.
        If nothing is passed, *None* is returned.
        
        Parameters
        ----------
        byNodes : Iterable[Element], optional
            Iterable of nodes defining the sub-graph. All edges between these nodes are conserved.
        byEdges : Iterable[Tuple[Element, Element, Element]], optional
            Iterable of edges defining the sub-graph, each defined as (node1, node2, edge key). All nodes involved with these edges, i.e. all node1's and node2's are preserved.
        
        Returns
        -------
        CommonGraphApi
            Copy of the sub-graph specified by either nodes or edges.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            if byNodes is not None:
                return self.copy(self.underlyingRawGraph.subgraph(byNodes))
                
            elif byEdges is not None:
                return self.copy(self.underlyingRawGraph.edge_subgraph(byEdges))
                
            else:
                return None
            
        # unknown implementation
        else:
            raise NotImplementedError
    
    def getEdgesElements(self) -> Set[Elements.Element]:
        """
        Get edge key elements of all edges.
        
        Returns
        -------
        Set[Element]
            Set of all edge's key elements, extracted from edge tuples of (node1, node2, edge key).
            Element objects which are the edge key of multiple edges are only returned once in the set.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        edges = self.getEdges()
        elementSet = set()
        for edge in edges:
            _, _, element = edge
            elementSet.add(element)
        return elementSet
    
    def copy(self, underlyingRawGraph = None) -> 'CommonGraphApi':
        """
        Shallow copy of the whole graph.
        
        However, some attributes are explicitly copied (although each attribute might in itself be shallowly copied):
            
            - .underlyingRawGraph
            - .name
            - .nodeCounts
            - .edgeCounts
            - .edgeElementCounts
        
        Parameters
        ----------
        underlyingRawGraph : :mod:`FEV_KEGG.Graph.Implementations`, optional
            If given, does not copy the underlying raw graph, but uses this one.
        
        Returns
        -------
        CommonGraphApi
            Shallow copy of the whole graph.
        """
        copy = self.__class__(underlyingRawGraph = underlyingRawGraph)
        if underlyingRawGraph is None:
            copy.underlyingRawGraph = self.underlyingRawGraph.copy()
        
        if copy.nodeCounts is not None:
            copy.nodeCounts = self.nodeCounts.copy()
        if copy.edgeCounts is not None:
            copy.edgeCounts = self.edgeCounts.copy()
        if copy.edgeElementCounts is not None:
            copy.edgeElementCounts = self.edgeElementCounts.copy()
        
        return copy

    def difference(self, subtrahend: 'Graph to be subtracted', subtractNodes = False, updateName = False) -> 'CommonGraphApi':
        """
        Difference between this graph and `subtrahend` graph, i.e. ``self - subtrahend``.
        
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Parameters
        ----------
        subtrahend : CommonGraphApi
            The graph to be subtracted.
        subtractNodes : bool, optional
            If *True*, also remove all nodes present in `subtrahend` from this graph.
            WARNING: This may remove edges that only exist in this graph, because they are removed with their associated node!
        updateName : bool, optional
            If *True*, update this graph's name.
        
        Returns
        -------
        CommonGraphApi
            A copy of this graph, containing all nodes which are present in this graph and all edges present in this graph, but which are **not** present in `subtrahend`.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        copy = self.copy()
        subtrahendEdges = subtrahend.getEdges()
        copy.removeEdges(subtrahendEdges)
        
        if (subtractNodes == True):
            subtrahendNodes = subtrahend.getNodes()
            copy.removeNodes(subtrahendNodes)
            
        # update name
        if updateName:
            copy.name = 'Difference ( [' + self.name + '], [' + subtrahend.name + '] )'
        
        return copy
    
    def intersection(self, withGraph: 'Graph to be intersected with, allows list of graphs', addCount = False, updateName = False) -> 'CommonGraphApi':
        """
        Intersection of this graph and the graph(s) in `withGraph`.
        
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Parameters
        ----------
        withGraph : CommonGraphApi or Iterable[CommonGraphApi]
            The graph(s) this graph is to be intersected with.
        addCount : bool, optional
            If *True*, the returned graph contains extra dicts:
            
                - graph.nodeCounts[node] = number of graphs which contained this node
                - graph.edgeCounts[(node, node, element)] = number of graphs which contained this edge 
                - graph.edgeElementCounts[element] = number of graphs which contained this element
        updateName : bool, optional
            If *True*, update this graph's name.
        
        Returns
        -------
        CommonGraphApi
            A copy of this graph, containing nodes and edges present in both this graph and the other graph(s).
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        
        # check if a list of graphs was passed
        if not isinstance(withGraph, Iterable):
            withGraph = [withGraph]
        
        nodesA = self.getNodes()
        edgesA = self.getEdges()
        if updateName:
            newGraphNameList = [self.name]
        
        if addCount is True:
            # count nodes and edges per graph
            nodesCount = dict.fromkeys(nodesA, 1)
            edgesCount = dict.fromkeys(edgesA, 1)
            elementSet = set()
            for edge in edgesA:
                _, _, element = edge
                elementSet.add(element)
            edgeElementsCount = dict.fromkeys(elementSet, 1)
        
        nodesIntersection = set(nodesA)
        edgesIntersection = set(edgesA)
        
        for graph in withGraph:
            # intersect set of nodes
            nodesB = graph.getNodes()
            
            if addCount is True:
                for node in nodesB:
                    nodesCount[node] = nodesCount.get(node, 0) + 1
            
            nodesIntersection = nodesIntersection.intersection(nodesB)
            
            # intersect set of edges
            edgesB = graph.getEdges()
            
            if addCount is True:
                
                elementSet = set()
                
                for edge in edgesB:
                    edgesCount[edge] = edgesCount.get(edge, 0) + 1
                    
                    _, _, element = edge
                    elementSet.add(element)
                
                for element in elementSet:
                    edgeElementsCount[element] = edgeElementsCount.get(element, 0) + 1
                
            edgesIntersection = edgesIntersection.intersection(edgesB)
            
            if updateName:
                newGraphNameList.append(graph.name)
        
        # add intersected nodes and edges to new graph
        newGraph = self.__class__()
        newGraph.addNodes(nodesIntersection)
        newGraph.addEdges(edgesIntersection)
        
        # update name
        if updateName:
            newGraph.name = 'Intersection ( [' + '], ['.join(newGraphNameList) + '] )'
        
        # if requested, add node counts
        if addCount is True:
            newGraph.nodeCounts = nodesCount
            newGraph.edgeCounts = edgesCount
            newGraph.edgeElementCounts = edgeElementsCount
        
        return newGraph
    
    def majorityIntersection(self, withGraph: 'Graph to be majority-intersected with, allows list of graphs', majorityPercentage = 51, addCount = False, updateName = False) -> 'CommonGraphApi':
        """
        Majority-Intersection of this graph and the graph(s) in `withGraph`.
        
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Parameters
        ----------
        withGraph : CommonGraphApi or Iterable[CommonGraphApi]
            The graph(s) this graph is to be intersected with.
        majorityPercentage : float, optional
            The majority percentage means 'at least x%' and is rounded up. For example 90% of 11 organisms (including the organism this method is called on) would be ceiling(9,9) = 10 organisms.
            If the rounded majority total effectively equated to 100% of all graphs, regular :func:`intersection` is called instead.
            If only one graph is passed in `withGraph` AND the rounded majority total effectively equates 1, regular :func:`union` is called instead.
        addCount : bool, optional
            If *True*, the returned graph contains extra dicts:
            
                - graph.nodeCounts[node] = number of graphs which contained this node
                - graph.edgeCounts[(node, node, element)] = number of graphs which contained this edge 
                - graph.edgeElementCounts[element] = number of graphs which contained this element
        updateName : bool, optional
            If *True*, update this graph's name.
        
        Returns
        -------
        CommonGraphApi
            A copy of this graph, containing all nodes and edges present in the majority of this graph and the other graph(s).
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        
        # check if majorityPercentage is sane
        if majorityPercentage <= 0 or majorityPercentage > 100:
            raise ValueError('Majority percentage is not a sane value (0 < percentage <= 100): ' + str(majorityPercentage))
        
        # check if a list of graphs was passed
        # calculate total number of graphs needed for majority
        if isinstance(withGraph, Iterable):
            withGraphLength = len( withGraph )
            majorityTotal = ceil((majorityPercentage/100) * (withGraphLength + 1))
            
            if majorityTotal >= (withGraphLength + 1): # effectively 100% majority needed, >= because of float rounding error
                return self.intersection(withGraph)
        else:
            if majorityPercentage <= 50: # effectively 'or', thus union
                return self.union(withGraph, addCount)
            else: # effectively 100% majority needed, thus intersection
                return self.intersection(withGraph)
        
        # multiple graphs passed, single graphs are completely handled above
        if updateName:
            newGraphNameList = [self.name]
        
        nodesA = self.getNodes()
        edgesA = self.getEdges()
        
        # count nodes and edges per graph
        nodesCount = dict.fromkeys(nodesA, 1)
        edgesCount = dict.fromkeys(edgesA, 1)
        
        if addCount is True:
            elementSet = set()
            for edge in edgesA:
                _, _, element = edge
                elementSet.add(element)
            edgeElementsCount = dict.fromkeys(elementSet, 1)
        
        for graph in withGraph:
            
            nodesB = graph.getNodes()
            for node in nodesB:
                nodesCount[node] = nodesCount.get(node, 0) + 1
            
            edgesB = graph.getEdges()
            
            if addCount is True:
                elementSet = set()
            
            for edge in edgesB:
                edgesCount[edge] = edgesCount.get(edge, 0) + 1
                
                if addCount is True:
                    _, _, element = edge
                    elementSet.add(element)
            
            if addCount is True:
                for element in elementSet:
                    edgeElementsCount[element] = edgeElementsCount.get(element, 0) + 1
            
            if updateName:
                newGraphNameList.append(graph.name)
        
        # remove nodes and edges with count < majorityTotal
        for item in list( nodesCount.items() ):
            node, count = item
            if count < majorityTotal: # count not high enough
                del nodesCount[node]
        
        for item in list( edgesCount.items() ):
            edge, count = item
            if count < majorityTotal: # count not high enough
                del edgesCount[edge]
        
        # add majority-intersected nodes and edges to new graph
        newGraph = self.__class__()
        newGraph.addNodes(nodesCount.keys())
        newGraph.addEdges(edgesCount.keys())
        
        # update name
        if updateName:
            newGraph.name = 'Majority-Intersection ' + str(majorityPercentage) + '% ( [' + '], ['.join(newGraphNameList) + '] )'
        
        # if requested, add node counts
        if addCount is True:
            newGraph.nodeCounts = nodesCount
            newGraph.edgeCounts = edgesCount
            newGraph.edgeElementCounts = edgeElementsCount
        
        return newGraph
        
    def union(self, withGraph: 'Graph to be unified with, allows list of graphs', addCount = False, updateName = False) -> 'CommonGraphApi':
        """
        Union of this graph and the graph(s) in `withGraph`.
        
        Parameters
        ----------
        withGraph : CommonGraphApi or Iterable[CommonGraphApi]
            The graph(s) this graph is to be unified with.
        addCount : bool, optional
            If *True*, the returned graph contains extra dicts:
            
                - graph.nodeCounts[node] = number of graphs which contained this node
                - graph.edgeCounts[(node, node, element)] = number of graphs which contained this edge 
                - graph.edgeElementCounts[element] = number of graphs which contained this element
        updateName : bool, optional
            If *True*, update this graph's name.
        
        Returns
        -------
        CommonGraphApi
            A copy of this graph, containing all nodes and all edges present in any of this graph or the other graph(s).
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        
        # check if a list of graphs was passed
        if not isinstance(withGraph, Iterable):
            withGraph = [withGraph]
        
        nodesA = self.getNodes()
        edgesA = self.getEdges()
        if updateName:
            newGraphNameList = [self.name]
        
        if addCount is True:
            # count nodes and edges per graph
            nodesCount = dict.fromkeys(nodesA, 1)
            edgesCount = dict.fromkeys(edgesA, 1)
            elementSet = set()
            for edge in edgesA:
                _, _, element = edge
                elementSet.add(element)
            edgeElementsCount = dict.fromkeys(elementSet, 1)
            
            for graph in withGraph:
                
                # unify set of nodes
                nodesB = graph.getNodes()
                for node in nodesB:
                    nodesCount[node] = nodesCount.get(node, 0) + 1
                
                # unify set of edges
                edgesB = graph.getEdges()
                
                elementSet = set()
                
                for edge in edgesB:
                    edgesCount[edge] = edgesCount.get(edge, 0) + 1
                    
                    _, _, element = edge
                    elementSet.add(element)
                
                for element in elementSet:
                    edgeElementsCount[element] = edgeElementsCount.get(element, 0) + 1
                
                if updateName:
                    newGraphNameList.append(graph.name)
            
            nodesUnion = nodesCount.keys()
            edgesUnion = edgesCount.keys()
            
        else:
            
            nodesUnion = set(nodesA)
            edgesUnion = set(edgesA)
            
            for graph in withGraph:
                
                # unify set of nodes
                nodesB = graph.getNodes()
                nodesUnion = nodesUnion.union(nodesB)
                
                # unify set of edges
                edgesB = graph.getEdges()
                edgesUnion = edgesUnion.union(edgesB)
                
                if updateName:
                    newGraphNameList.append(graph.name)
        
        # add unified nodes and edges to new graph
        newGraph = self.__class__()
        newGraph.addNodes(nodesUnion)
        newGraph.addEdges(edgesUnion)
        
        # update name
        if updateName:
            newGraph.name = 'Union ( [' + '], ['.join(newGraphNameList) + '] )'
        
        # if requested, add node counts
        if addCount is True:
            newGraph.nodeCounts = nodesCount
            newGraph.edgeCounts = edgesCount
            newGraph.edgeElementCounts = edgeElementsCount 
        
        return newGraph
        
    
    def __eq__(self, other: object):
        """
        Determine equality of two graphs.
        
        Parameters
        ----------
        other : object
            The object to compare this graph with.
        
        Returns
        -------
        bool
            Both graphs are considered equal, if they have identical memory addresses OR (the same class AND the same number of nodes and edges AND they are ismorphic).
            WARNING: isomorphism check is NP-hard!
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        if self is other: # identical object -> True
            return True
        
        if isinstance(self, other.__class__): # same class
            
            # NetworkX was chosen as graph implementation
            if self.__class__.implementationLib == NetworkX:
                
                if self.underlyingRawGraph.order() == other.underlyingRawGraph.order() and self.underlyingRawGraph.size() == other.underlyingRawGraph.size(): # same number of nodes and edges (weight 1)
                    
                    if len( set(self.underlyingRawGraph.nodes).symmetric_difference( other.underlyingRawGraph.nodes ) ) == 0: # same node set
                        
                        if len( set(self.underlyingRawGraph.edges).symmetric_difference( other.underlyingRawGraph.edges ) ) == 0: # same edge set
                            
                            return True # -> True
                
            # unknown implementation
            else:
                raise NotImplementedError
        
        return False # everything else -> False
        
    def __ne__(self, other: object):
        """
        Determine non-equality of two graphs.
        
        This simply negates :func:`__eq__`.
        
        Parameters
        ----------
        other : object
            The object to compare this graph with.
        
        Returns
        -------
        bool
            Both graphs are considered inequal, if they do not have identical memory addresses NOR (the same class AND the same number of nodes and edges AND they are ismorphic).
            WARNING: isomorphism check is NP-hard!
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        return not self == other
    
    def replaceNode(self, oldNode: Elements.Element, newNode: Elements.Element):
        """
        Replaces a certain node, if present, with another node.
        
        Silently ignores non-existing nodes.
        
        Parameters
        ----------
        oldNode : Element
            Node to be replaced.
        newNode : Element
            Node used to replace the `oldNode`.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        
        if oldNode.__class__ is not newNode.__class__:
            raise TypeError('classes of nodes do not match')
        
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            networkx.relabel_nodes(self.underlyingRawGraph, {oldNode : newNode}, copy = False)
            
        # unknown implementation
        else:
            raise NotImplementedError
        
    def replaceEdgeElement(self, edge: Tuple[Elements.Element, Elements.Element, Elements.Element], newElement: Elements.Element, bothDirections: bool = False):
        """
        Replaces a certain edge key element, if the edge is present, with another element.
        
        Silently ignores non-existing edge, especially never adds the new edge. Treats both directions independently.
        
        Parameters
        ----------
        edge : Tuple[Element, Element, Element]
            Tuple representing the edge which key element is to be replaced.
        newElement : Element
            The element to replace the edge's former key element.
        bothDirections : bool, optional
            If *True*, automatically replace the edge key element of both directions. If the other direction does not exist, nothing happens.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationLib`.
        """
        
        node1, node2, oldElement = edge
        
        if oldElement.__class__ is not newElement.__class__:
            raise TypeError('classes of edge elements do not match')
        
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            if self.underlyingRawGraph.has_edge(node1, node2, oldElement):
                self.removeEdge(node1, node2, oldElement, bothDirections = False)
                self.addEdge(node1, node2, newElement, isReversible = False)
                
            if bothDirections == True:
                if self.underlyingRawGraph.has_edge(node2, node1, oldElement):
                    self.removeEdge(node2, node1, oldElement, bothDirections = False)
                    self.addEdge(node2, node1, newElement, isReversible = False)
            
        # unknown implementation
        else:
            raise NotImplementedError
        
        
        
        

class DirectedMultiGraph(CommonGraphApi):
    
    implementationGraph = MultiDiGraph
    """
    Implementation library's class for a directed graph.
    """
    
    def __init__(self, underlyingRawGraph: 'implementationGraph' = None):
        """
        Represents a directed multigraph.
        
        Parameters
        ----------
        underlyingRawGraph : :attr:`implementationGraph`, optional
            If not *None*, copies `underlyingRawGraph` and stores it for this object.
        
        Attributes
        ----------
        self.underlyingRawGraph : :mod:`FEV_KEGG.Graph.Implementations`
            The actual graph containing the data. This is dependant on the implementation chosen in :attr:`implementationLib`.
        self.name : str
            Custom name of the graph. This is often set, but not necessary in any calculations.
        self.nodeCounts : Dict[Element, int], optional
            Number of precursor graphs which contained certain :class:`Element` nodes still in this graph. *None* by default.
        self.edgeCounts : Dict[Tuple[Element, Element, Element], int], optional
            Number of precursor graphs which contained a certain edge (a Tuple of three :class:`Element`) still in this graph. *None* by default.
        self.edgeElementCounts : Dict[Element, int], optional
            Number of precursor graphs which contained certain :class:`Element` edge keys still in this graph. *None* by default.
        """
        CommonGraphApi.__init__(self, underlyingRawGraph)
        if underlyingRawGraph == None:
            self.underlyingRawGraph = self.__class__.implementationGraph()
    
    def getUnidirectionalEdges(self) -> Set[Tuple[Elements.Element, Elements.Element, Elements.Element]]:
        """
        Get all edges which are unidirectional only.
        
        Returns
        -------
        Set[Tuple[Element, Element, Element]]
            Set of all edge tuples (node1, node2, edge key) that have only one direction, i.e. there is no other edge tuple in reverse direction (node2, node1, edge key).
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationGraph`.
        """
        undirectedGraphKeeping = self.toUndirectedGraph(True)
        undirectedGraph = self.toUndirectedGraph(False)
        
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            differenceGraph = networkx.algorithms.operators.difference(undirectedGraphKeeping.underlyingRawGraph, undirectedGraph.underlyingRawGraph)
            edgeList = differenceGraph.edges(keys=True)
            return edgeList
            
        # unknown implementation
        else:
            raise NotImplementedError
    
    def getUnidirectionalEdgesElements(self) -> Set[Elements.Element]:
        """
        Get the edge key elements of all edges which are unidirectional only.
        
        Returns
        -------
        Set[Element]
            Set of all edge key elements of edges returned by :func:`getUnidirectionalEdges`.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationGraph`.
        """
        unidirectionalEdges = self.getUnidirectionalEdges()
        elementSet = set()
        for edge in unidirectionalEdges:
            _, _, element = edge
            elementSet.add(element)
        return elementSet
        
    def toUndirectedGraph(self, keepUnidirectionalEdges = False) -> 'UndirectedMultiGraph':
        """
        Create undirected graph from this directed graph.
        
        Parameters
        ----------
        keepUnidirectionalEdges : bool, optional
            If *True*, treat unidirectional edges in `directedMultiGraph` as undirected edges, thus keep them for this graph.
            If *False* (default), undirected edges are only created if there are edges for both directions in `directedMultiGraph`.
        
        Returns
        -------
        UndirectedMultiGraph
            Undirected graph converted from this directed graph.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationGraph`.
        """
        return UndirectedMultiGraph.fromDirectedMultiGraph(self, keepUnidirectionalEdges)



        
class UndirectedMultiGraph(CommonGraphApi):

    implementationGraph = MultiGraph
    """
    Implementation library's class for an undirected graph.
    """
    
    def __init__(self, underlyingRawGraph: 'implementationGraph' = None):
        """
        Represents an undirected multi graph.
        
        Parameters
        ----------
        underlyingRawGraph : :attr:`implementationGraph`, optional
            If not *None*, copies `underlyingRawGraph` and stores it for this object.
        
        Attributes
        ----------
        self.underlyingRawGraph : :mod:`FEV_KEGG.Graph.Implementations`
            The actual graph containing the data. This is dependant on the implementation chosen in :attr:`implementationLib`.
        self.name : str
            Custom name of the graph. This is often set, but not necessary in any calculations.
        self.nodeCounts : Dict[Element, int], optional
            Number of precursor graphs which contained certain :class:`Element` nodes still in this graph. *None* by default.
        self.edgeCounts : Dict[Tuple[Element, Element, Element], int], optional
            Number of precursor graphs which contained a certain edge (a Tuple of three :class:`Element`) still in this graph. *None* by default.
        self.edgeElementCounts : Dict[Element, int], optional
            Number of precursor graphs which contained certain :class:`Element` edge keys still in this graph. *None* by default.
        """
        CommonGraphApi.__init__(self, underlyingRawGraph)
        if underlyingRawGraph == None:
            self.underlyingRawGraph = self.__class__.implementationGraph()
        
    @classmethod
    def fromDirectedMultiGraph(cls, directedMultiGraph: DirectedMultiGraph, keepUnidirectionalEdges = False):
        """
        Create undirected graph from a directed graph.
        
        Parameters
        ----------
        directedMultiGraph : DirectedMultiGraph
            Directed graph to use for conversion.
        keepUnidirectionalEdges : bool, optional
            If *True*, treat unidirectional edges in `directedMultiGraph` as undirected edges, thus keep them for this graph.
            If *False* (default), undirected edges are only created if there are edges for both directions in `directedMultiGraph`.
        
        Returns
        -------
        UndirectedMultiGraph
            Undirected graph converted from `directedMultiGraph`.
        
        Raises
        ------
        NotImplementedError
            If this function has not been adapted to the chosen graph implementation, yet. See :attr:`implementationGraph`.
        """
        instance = cls()
        
        # if the graph has a pathway set it was derived from, copy it, too
        if hasattr(directedMultiGraph, 'pathwaySet'):
            instance.pathwaySet = directedMultiGraph.pathwaySet.copy()
        
        # NetworkX was chosen as graph implementation
        if directedMultiGraph.__class__.implementationGraph == MultiDiGraph:
            
            instance.underlyingRawGraph = directedMultiGraph.underlyingRawGraph.to_undirected(reciprocal = not keepUnidirectionalEdges)
        
        # unknown implementation
        else:
            raise NotImplementedError
        
        return instance
    