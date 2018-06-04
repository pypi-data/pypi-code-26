from FEV_KEGG.lib.Biopython.KEGG.KGML import KGML_pathway
from typing import List, Set, Tuple, Iterable, Dict

import FEV_KEGG.Graph.Elements as Elements
from FEV_KEGG.Graph.Models import DirectedMultiGraph
from FEV_KEGG.KEGG import Database
from FEV_KEGG.settings import verbosity as init_verbosity


class SubstrateReactionGraph(DirectedMultiGraph):
    
    def __init__(self, underlyingRawGraph = None, pathwaySet = None):
        """
        Directed graph with :class:`Substrate` nodes and :class:`Reaction` edges, allowing multiple edges.
        
        Links two :class:`FEV_KEGG.Graph.Elements.Substrate` (compound or glycan) nodes with each :class:`FEV_KEGG.Graph.Elements.Reaction` edge they occur in. 
        Substrates have to occur on different sides of the reaction, one being a substrate, the other being a product.
        Reversible reactions will get two edges with swapped roles of substrate/product.
        There may be other substrates/products in the same reaction, they will be linked with another edge.
        
        For example A1 + A2 -> B1 + B2 will yield four edges: (A1, B1); (A1, B2); (A2, B1); (A2, B2).
        Making this reaction reversible would yield eight edges, because each tuple will be swapped to form the other direction.
        
        Parameters
        ----------
        underlyingRawGraph : :mod:`FEV_KEGG.Graph.Implementations`
            If not *None*, copies `underlyingRawGraph` and stores it for this object.
        pathwaySet : Set[KGML_pathway.Pathway], optional
            Set of pathways this graph was derived from. Especially useful for e.g. :func:`Conversion.SubstrateReactionGraph2SubstrateGeneGraph`.
            
        Attributes
        ----------
        self.underlyingRawGraph : :mod:`FEV_KEGG.Graph.Implementations`
            The actual graph containing the data. This is dependant on the implementation.
        self.name : str
            Custom name of the graph. This is often set, but not necessary in any calculations.
        self.pathwaySet : Set[KGML_pathway.Pathway]
            Set of pathways this graph was derived from. Especially useful for e.g. :func:`Conversion.SubstrateReactionGraph2SubstrateGeneGraph`.
        self.substrateCounts : Dict[Substrate, int], optional
            Number of precursor graphs which contained certain :class:`Substrate` nodes still in this graph. *None* by default.
        self.reactionCounts : Dict[Elements.Reaction, int], optional
            Number of precursor graphs which contained certain :class:`Reaction` edge keys still in this graph. *None* by default.
        """
        super().__init__(underlyingRawGraph)
        
        if pathwaySet == None:
            self.pathwaySet = set() # set of pathways objects (KGML_pathway.Pathway) that contributed to this graph
        else:
            self.pathwaySet = pathwaySet.copy()
    
    @property
    def substrateCounts(self) -> Dict[Elements.Substrate, int]:
        """
        Number of precursor graphs which contained certain :class:`Substrate` nodes still in this graph. *None* by default.
        """
        return self.nodeCounts
    
    @property
    def reactionCounts(self) -> Dict[Elements.Substrate, int]:
        """
        Number of precursor graphs which contained certain :class:`Reaction` edge keys still in this graph. *None* by default.
        """
        return self.edgeElementCounts
    
    @staticmethod
    def fromPathway(pathway: Set[KGML_pathway.Pathway]):
        """
        Create :class:`SubstrateReactionGraph` from certain pathways.
        
        Parameters
        ----------
        pathway : Set[KGML_pathway.Pathway] or KGML_pathway.Pathway
            Pathway(s) to use for creating the graph.
        
        Returns
        -------
        SubstrateReactionGraph
            A new substrate-reaction graph.
        """
        if isinstance(pathway, KGML_pathway.Pathway): # only single pathway given
            return Conversion.KeggPathway2SubstrateReactionGraph(pathway)
        else: # multiple pathways given
            return Conversion.KeggPathwaySet2SubstrateReactionGraph(pathway)
    
    def addReaction(self, substrate: Elements.Substrate, product: Elements.Substrate, reaction: Elements.Reaction, isReversible: bool = False):
        """
        Add a `reaction` edge between `substrate` and `product`.
        
        Parameters
        ----------
        substrate : Substrate
            Substrate from which the `reaction` edge starts. Automatically added, if not already in the graph.
        product : Substrate
            Substrate where the `reaction` edge ends. Automatically added, if not already in the graph.
        reaction : Elements.Reaction
            Reaction with which the new edge is to be annotated, as its edge key.
        isReversible : bool, optional
            If *True*, add reaction in both directions.
        """
        super().addEdge(substrate, product, reaction, isReversible) # automatically creates node, if not already present
        
    def getUnidirectionalReactions(self) -> Set[Elements.Reaction]:
        """
        Get the reactions of all edges which are unidirectional only.
        
        Returns
        -------
        Set[Elements.Reaction]
            Set of all reactions which are edge keys of edges that have only one direction, i.e. there is no other edge in reverse direction with the same reaction edge key.
        """
        return self.getUnidirectionalEdgesElements()
    
    def getReactions(self) -> Set[Elements.Reaction]:
        """
        Get all reactions.
        
        Returns
        -------
        Set[Elements.Reaction]
            Set of all reaction edge keys in this graph.
        """
        return self.getEdgesElements()
    
    def copy(self, underlyingRawGraph = None):
        """
        Shallow copy of the whole graph.
        
        However, some attributes are explicitly copied (although each attribute might in itself be shallowly copied):
        
            - .underlyingRawGraph
            - .name
            - .nodeCounts
            - .edgeCounts
            - .edgeElementCounts
            - .pathwaySet
        
        Parameters
        ----------
        underlyingRawGraph : :mod:`FEV_KEGG.Graph.Implementations`, optional
            If given, does not copy the underlying raw graph, but uses this one.
        
        Returns
        -------
        SubstrateReactionGraph
            Shallow copy of the whole graph.
        """
        copy = super().copy(underlyingRawGraph)
        copy.pathwaySet = self.pathwaySet.copy()
        
        return copy
        

class SubstrateGeneGraph(DirectedMultiGraph):
    
    def __init__(self, underlyingRawGraph: 'implementationGraph' = None):
        """
        Directed graph with :class:`Substrate` nodes and :class:`GeneID` edges, allowing multiple edges.
            
        Links two :class:`FEV_KEGG.Graph.Elements.Substrate` (compound or glycan) nodes with each :class:`FEV_KEGG.Graph.Elements.GeneID` edge, associated with a :class:`FEV_KEGG.Graph.Elements.Reaction` they occur in.
        
        Attributes
        ----------
        self.underlyingRawGraph : :mod:`FEV_KEGG.Graph.Implementations`
            The actual graph containing the data. This is dependant on the implementation.
        self.name : str
            Custom name of the graph. This is often set, but not necessary in any calculations.
        self.substrateCounts : Dict[Substrate, int], optional
            Number of precursor graphs which contained certain :class:`Substrate` nodes still in this graph. *None* by default.
        self.geneCounts : Dict[Elements.GeneID, int], optional
            Number of precursor graphs which contained certain :class:`GeneID` edge keys still in this graph. *None* by default.
        """
        super().__init__(underlyingRawGraph)
    
    @property
    def substrateCounts(self):
        """
        Number of precursor graphs which contained certain :class:`Substrate` nodes still in this graph. *None* by default.
        """
        return self.nodeCounts
    
    @property
    def geneCounts(self):
        """
        Number of precursor graphs which contained certain :class:`GeneID` edge keys still in this graph. *None* by default.
        """
        return self.edgeElementCounts
    
    @staticmethod
    def fromSubstrateReactionGraph(substrateReactionGraph: SubstrateReactionGraph):
        """
        Create :class:`SubstrateGeneGraph` from a :class:`SubstrateReactionGraph`.
        
        Replaces reactions with their associated genes. Splits reactions associated with several genes. Deduplicates reactions associated with the same gene.
        See the structure of a KEGG KGML pathway description file for further insight.
        
        Parameters
        ----------
        substrateReactionGraph : SubstrateReactionGraph
            The substrate-reaction graph to use for creating this graph. Apart from the graph structure itself, its attribute :attr:`SubstrateReactionGraph.pathwaySet` is needed!
        
        Returns
        -------
        SubstrateGeneGraph
            A new substrate-gene graph.
        """
        return Conversion.SubstrateReactionGraph2SubstrateGeneGraph(substrateReactionGraph)
    
    def getGenes(self) -> Set[Elements.GeneID]:
        """
        Get all genes.
        
        Returns
        -------
        Set[GeneID]
            Set of all genes in this graph.
        """
        return self.getEdgesElements()
    
    def addGene(self, substrate: Elements.Substrate, product: Elements.Substrate, geneID: Elements.GeneID, isReversible: bool = False):
        """
        Add an `geneID` between the substrates `substrate` and `product`.
        
        Parameters
        ----------
        substrate : Substrate
            Automatically added, if not already in the graph.
        product : Substrate
            Automatically added, if not already in the graph.
        geneID : GeneID
        isReversible : bool, optional
            If *True*, add in both directions, swapping `substrate` and `product`.
        """
        super().addEdge(substrate, product, geneID, isReversible) # automatically creates node, if not already present
    
    def removeGenes(self, geneIDs: Iterable[Elements.GeneID]):
        """
        Remove all occurences of certain genes.
        
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Parameters
        ----------
        geneIDs : Iterable[GeneID]
            Iterable of genes to be completely removed from the graph.
        """
        super().removeEdgesByElement(geneIDs)
    
    def removeAllGenesExcept(self, genesToKeep: Iterable[Elements.GeneID]):
        """
        Remove all genes which are **not** in `genesToKeep`.
        
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Parameters
        ----------
        genesToKeep : Iterable[GeneID]
            Iterable of genes to keep in the graph. All other genes are removed.
        """
        genesToKeepSet = set()
        genesToKeepSet.update(genesToKeep)
        genesToRemove = self.getGenes()
        genesToRemove.difference_update(genesToKeepSet)
        self.removeGenes(genesToRemove)
    
    def removeGeneEdge(self, substrate: Elements.Substrate, product: Elements.Substrate, gene: Elements.GeneID, bothDirections: bool = False):
        """
        Remove a `gene` between `substrate` and `product`.
        
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Parameters
        ----------
        substrate : Substrate
            Not removed from the graph.
        product : Substrate
            Not removed from the graph.
        gene : GeneID
        bothDirections : bool, optional
            If *True*, remove both directions, swapping `substrate` and `product`.
        """
        super().removeEdge(substrate, product, gene, bothDirections)
    
    def removeGeneEdges(self, geneEdges: List[Tuple[Elements.Substrate, Elements.Substrate, Elements.GeneID]]):
        """
        Remove all genes in certain edges.
        
        Parameters
        ----------
        geneEdges : List[Tuple[Substrate, Substrate, GeneID]]
            List of tuples, each describing an edge to be removed from the graph. If an edge to be removed does not exist, the next edge will be tried, without any error message.
        """
        for geneEdge in geneEdges:
            substrate, product, gene = geneEdge
            self.removeGeneEdge(substrate, product, gene, bothDirections = False)
    
    def getUnidirectionalGenes(self) -> Set[Elements.GeneID]:
        """
        Get all genes which have only one direction.
        
        Returns
        -------
        Set[GeneID]
            Set of genes which take part in an edge with only one direction. Meaning there is no edge with the opposite direction between the same substrated, annotated with the same gene.
        """
        return self.getUnidirectionalEdgesElements()
    
    def getMultifunctionalGeneEdges(self) -> List[Tuple[Elements.Substrate, Elements.Substrate, Elements.GeneID]]:
        """
        Get all edges annotated with a gene associated with more than one EC number.
        
        Returns
        -------
        List[Tuple[Substrate, Substrate, GeneID]]
            List of all edge tuples where its gene, represented by a :class:`GeneID`, is associated with more than one EC number.
        
        Warnings
        --------
        Parses Database, this is slow and expensive!
        """
        multifunctionalEdgeList = []
        edgeList = self.getEdges()
        
        geneIDs = [x for _,_,x in edgeList]
        geneDict = Database.getGeneBulk(geneIDs)            
            
        for edge in edgeList:
            _, _, element = edge
            
            gene = geneDict.get(element.geneIDString, None)
            
            if gene is None: # should not happen, but might
                continue
            
            ecNumbersList = Elements.Enzyme.fromGene(gene).ecNumbers
            
            if len(ecNumbersList) > 1:
                multifunctionalEdgeList.append(edge)
        
        return multifunctionalEdgeList
    
    def getMultifunctionalGenes(self) -> Set[Elements.GeneID]:
        """
        Get all genes which are associated with more than one EC number.
        
        Returns
        -------
        Set[GeneID]
            Set of genes associated with more than one EC number.

        Warnings
        --------
        Parses Database, this is slow and expensive!
        """
        genes = set()
        edges = self.getMultifunctionalGeneEdges()
        for edge in edges:
            _, _, gene = edge
            genes.add(gene)
        
        return genes
        
    def removeMultifunctionalGenes(self):
        """
        Remove genes associated with more than one EC number. 
        
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Warnings
        --------
        Parses Database, this is slow and expensive!
        """
        multifunctionalEdges = self.getMultifunctionalGeneEdges()
        super().removeEdges(multifunctionalEdges)


class SubstrateEnzymeGraph(DirectedMultiGraph):
    
    def __init__(self, underlyingRawGraph: 'implementationGraph' = None):
        """
        Directed graph with :class:`Substrate` nodes and :class:`Enzyme` edges, allowing multiple edges.
        
        Links two :class:`FEV_KEGG.Graph.Elements.Substrate` (compound or glycan) nodes with each :class:`FEV_KEGG.Graph.Elements.Enzyme` edge, associated with a :class:`FEV_KEGG.Graph.Elements.GeneID`, associated with a :class:`FEV_KEGG.Graph.Elements.Reaction` they occur in.
        Replaces each GeneID object with its associated Enzyme object.
        
        Attributes
        ----------
        self.underlyingRawGraph : :mod:`FEV_KEGG.Graph.Implementations`
            The actual graph containing the data. This is dependant on the implementation.
        self.name : str
            Custom name of the graph. This is often set, but not necessary in any calculations.
        self.substrateCounts : Dict[Substrate, int], optional
            Number of precursor graphs which contained certain :class:`Substrate` nodes still in this graph. *None* by default.
        self.enzymeCounts : Dict[Elements.Enzyme, int], optional
            Number of precursor graphs which contained certain :class:`Enzyme` edge keys still in this graph. *None* by default.
        self.indexOnEC : Dict[EcNumber, Set[Enzyme]]
            Index to find all enzymes by a certain EC number.
        self.indexOnGeneID : Dict[GeneID, Enzyme]
            Index to find an enzyme by its gene ID. An enzyme is uniquely identified by its gene ID.
        
        Warnings
        --------
        Automatically parses genes from KEGG, this is slow and expensive!
        """
        super().__init__(underlyingRawGraph)
        self.indexOnEC = dict() # EcNumber -> set{Enzyme, Enzyme, ...}
        self.indexOnGeneID = dict() # GeneID -> Enzyme
    
    @property
    def substrateCounts(self):
        """
        Number of precursor graphs which contained certain :class:`Substrate` nodes still in this graph. *None* by default.
        """
        return self.nodeCounts
    
    @property
    def enzymeCounts(self):
        """
        Number of precursor graphs which contained certain :class:`Enzyme` edge keys still in this graph. *None* by default.
        """
        return self.edgeElementCounts
    
    # override parent class methods, to keep index up-to-date
    def addEdge(self, node1:Elements.Element, node2:Elements.Element, key:Elements.Element, isReversible:bool=False):
        """
        Automatically updates the indices. See :class:`FEV_KEGG.Graph.Models.DirectedMultiGraph` for the original function. 
        """
        if isinstance(key, Elements.Enzyme):
            self.addEnzyme(node1, node2, key, isReversible)
        else:
            super().addEdge(node1, node2, key, isReversible)
    
    def addEdges(self, edges: List[Tuple[Elements.Element, Elements.Element, Elements.Element]]):
        """
        Automatically updates the indices. See :class:`FEV_KEGG.Graph.Models.DirectedMultiGraph` for the original function. 
        """
        for substrate, product, key in edges:
            if isinstance(key, Elements.Enzyme):
                self.addEnzyme(substrate, product, key, isReversible = False)
            else:
                super().addEdge(substrate, product, key, isReversible = False)
    
    def removeEdge(self, node1:Elements.Element, node2:Elements.Element, key:Elements.Element, bothDirections:bool=False):
        """
        Automatically updates the indices. See :class:`FEV_KEGG.Graph.Models.DirectedMultiGraph` for the original function. 
        """
        if isinstance(key, Elements.Enzyme):
            self.removeEnzymeEdge(node1, node2, key, bothDirections)
        else:
            super().removeEdge(node1, node2, key, bothDirections)
        
    def removeEdges(self, edges:List[Tuple]):
        """
        Automatically updates the indices. See :class:`FEV_KEGG.Graph.Models.DirectedMultiGraph` for the original function. 
        """
        self.removeEnzymeEdges(edges)
        
    def removeEdgesByElement(self, elements:Iterable[Elements.Element]):
        """
        Automatically updates the indices. See :class:`FEV_KEGG.Graph.Models.DirectedMultiGraph` for the original function. 
        """
        self.removeEnzymes(elements)
    
    
    @staticmethod
    def fromSubstrateGeneGraph(substrateGeneGraph: SubstrateGeneGraph):
        """
        Create :class:`SubstrateEnzymeGraph` from a :class:`SubstrateGeneGraph`.
        
        Replaces reactions with their associated genes. Splits reactions associated with several genes. Deduplicates reactions associated with the same gene.
        See the structure of a KEGG KGML pathway description file for further insight.
        
        Parameters
        ----------
        substrateGeneGraph : SubstrateGeneGraph
            The substrate-gene graph to use for creating this graph. Apart from the graph structure itself, downloads from KEGG GENE are needed!
        
        Returns
        -------
        SubstrateEnzymeGraph
            A new substrate-enzyme graph.
        
        Warnings
        --------
        Automatically parses genes from KEGG, this is slow and expensive!
        """
        return Conversion.SubstrateGeneGraph2SubstrateEnzymeGraph(substrateGeneGraph)
    
    def getEnzymes(self) -> Set[Elements.Enzyme]:
        """
        Get all enzymes.
        
        Returns
        -------
        Set[Enzyme]
            Set of all enzymes in this graph.
        """
        return self.getEdgesElements()
    
    def addEnzyme(self, substrate: Elements.Substrate, product: Elements.Substrate, enzyme: Elements.Enzyme, isReversible: bool = False):
        """
        Add an `enzyme` between the substrates `substrate` and `product`.
        
        Automatically updates indices.
        
        Parameters
        ----------
        substrate : Substrate
            Automatically added, if not already in the graph.
        product : Substrate
            Automatically added, if not already in the graph.
        enzyme : Enzyme
        isReversible : bool, optional
            If *True*, add in both directions, swapping `substrate` and `product`.
        """
        super().addEdge(substrate, product, enzyme, isReversible) # automatically creates node, if not already present
        
        # add Enzyme to EC index
        for ecNumber in enzyme.ecNumbers:
            enzymeSet = self.indexOnEC.get(ecNumber, None)
            if enzymeSet is None:
                newEnzymeSet = set()
                newEnzymeSet.add(enzyme)
                self.indexOnEC[ecNumber] = newEnzymeSet
            else:
                enzymeSet.add(enzyme)
                
        # add Enzyme to GeneID index
        self.indexOnGeneID[enzyme.geneID] = enzyme
    
    def removeEnzymes(self, enzymes: Iterable[Elements.Enzyme]):
        """
        Remove all occurences of certain enzymes.
        
        Automatically updates indices.
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Parameters
        ----------
        enzymes : Iterable[Enzyme]
            Iterable of enzymes to be completely removed from the graph.
        """
        super().removeEdgesByElement(enzymes)
        
        for enzyme in enzymes:
            # remove Enzyme from EC index
            for ecNumber in enzyme.ecNumbers:
                enzymeSet = self.indexOnEC.get(ecNumber, None)
                if enzymeSet is not None:
                    enzymeSet.discard(enzyme)
                    if len( enzymeSet ) == 0: # enzyme set is now empty, remove it completely
                        del self.indexOnEC[ecNumber]
            
            # remove Enzyme from GeneID index
            if self.indexOnGeneID.get(enzyme.geneID, None) is not None:
                del self.indexOnGeneID[enzyme.geneID]
    
    def removeAllEnzymesExcept(self, enzymesToKeep: Iterable[Elements.Enzyme]):
        """
        Remove all enzymes which are **not** in `enzymesToKeep`.
        
        Automatically updates indices.
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Parameters
        ----------
        enzymesToKeep : Iterable[Enzyme]
            Iterable of enzymes to keep in the graph. All other enzymes are removed.
        """
        enzymesToKeepSet = set()
        enzymesToKeepSet.update(enzymesToKeep)
        enzymesToRemove = self.getEnzymes()
        enzymesToRemove.difference_update(enzymesToKeepSet)
        self.removeEnzymes(enzymesToRemove)
    
    def removeEnzymeEdge(self, substrate: Elements.Substrate, product: Elements.Substrate, enzyme: Elements.Enzyme, bothDirections: bool = False):
        """
        Remove an `enzyme` between `substrate` and `product`.
        
        Automatically updates indices.
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Parameters
        ----------
        substrate : Substrate
            Not removed from the graph.
        product : Substrate
            Not removed from the graph.
        enzyme : Enzyme
        bothDirections : bool, optional
            If *True*, remove both directions, swapping `substrate` and `product`.
        """
        super().removeEdge(substrate, product, enzyme, bothDirections)
        
        # remove Enzyme from EC index
        for ecNumber in enzyme.ecNumbers:
            enzymeSet = self.indexOnEC.get(ecNumber, None)
            if enzymeSet is not None:
                enzymeSet.discard(enzyme)
                if len( enzymeSet ) == 0: # enzyme set is now empty, remove it completely
                    del self.indexOnEC[ecNumber]
        
        # remove Enzyme from GeneID index
        if self.indexOnGeneID.get(enzyme.geneID, None) is not None:
            del self.indexOnGeneID[enzyme.geneID]
    
    def removeEnzymeEdges(self, enzymeEdges: List[Tuple[Elements.Substrate, Elements.Substrate, Elements.Enzyme]]):
        """
        Remove all enzymes in certain edges.
        
        Automatically updates indices.
        
        Parameters
        ----------
        enzymeEdges : List[Tuple[Substrate, Substrate, Enzyme]]
            List of tuples, each describing an edge to be removed from the graph. If an edge to be removed does not exist, the next edge will be tried, without any error message.
        """
        for enzymeEdge in enzymeEdges:
            substrate, product, enzyme = enzymeEdge
            self.removeEnzymeEdge(substrate, product, enzyme, bothDirections = False)
    
    def getUnidirectionalEnzymes(self) -> Set[Elements.Enzyme]:
        """
        Get all enzymes which have only one direction.
        
        Returns
        -------
        Set[Enzyme]
            Set of enzymes which take part in an edge with only one direction. Meaning there is no edge with the opposite direction between the same substrated, annotated with the same enzyme.
        """
        return self.getUnidirectionalEdgesElements()
    
    def getMultifunctionalEnzymeEdges(self) -> List[Tuple[Elements.Substrate, Elements.Substrate, Elements.Enzyme]]:
        """
        Get all edges annotated with an enzyme associated with more than one EC number.
        
        Returns
        -------
        List[Tuple[Substrate, Substrate, Enzyme]]
            List of all edge tuples where its enzyme is associated with more than one EC number.
        """
        multifunctionalEdgeList = []
        edgeList = self.getEdges()
        for edge in edgeList:
            _, _, element = edge
            
            ecNumbersList = element.ecNumbers
            
            if len(ecNumbersList) > 1:
                multifunctionalEdgeList.append(edge)
        
        return multifunctionalEdgeList
    
    def getMultifunctionalEnzymes(self) -> Set[Elements.Enzyme]:
        """
        Get all enzymes which are associated with more than one EC number.
        
        Returns
        -------
        Set[Enzyme]
            Set of enzymes associated with more than one EC number.
        """
        enzymes = set()
        edges = self.getMultifunctionalEnzymeEdges()
        for edge in edges:
            _, _, enzyme = edge
            enzymes.add(enzyme)
        
        return enzymes
        
    def removeMultifunctionalEnzymes(self):
        """
        Remove enzymes associated with more than one EC number. 
        
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        """
        multifunctionalEdges = self.getMultifunctionalEnzymeEdges()
        self.removeEnzymeEdges(multifunctionalEdges)
        
    def getEnzymesForEcNumber(self, ecNumber: Elements.EcNumber) -> Set[Elements.Enzyme]:
        """
        Get enzymes associated with a certain EC number.
        
        Parameters
        ----------
        ecNumber : EcNumber
        
        Returns
        -------
        Set[Enzyme]
            Set of enzymes associated with the EC number in the `ecNumber` parameter. If there is no such EC number, returns an empty set.
        """
        return self.indexOnEC.get(ecNumber, set())
    
    def getGeneIDsForEcNumber(self, ecNumber: Elements.EcNumber) -> Set[Elements.GeneID]:
        """
        Get genes associated with a certain EC number.
        
        Parameters
        ----------
        ecNumber : EcNumber
        
        Returns
        -------
        Set[GeneID]
            Set of genes associated with the EC number in the `ecNumber` parameter. If there is no such EC number, returns an empty set.
        """
        enzymes = self.getEnzymesForEcNumber(ecNumber)
        
        geneIDs = set()
        for enzyme in enzymes:
            geneID = enzyme.geneID
            geneIDs.add(geneID)
        
        return geneIDs
    
    def getEnzymeForGeneID(self, geneID: Elements.GeneID) -> Elements.Enzyme:
        """
        Get the enzyme uniquely identified with `geneID`.
        
        Parameters
        ----------
        geneID : GeneID
            The gene encoding the enzyme.
        
        Returns
        -------
        Enzyme
            The enzyme in this graph identified by the given `geneID`. If there is no such `geneID`, returns *None*.
        """
        return self.indexOnGeneID.get(geneID, None)
    
    def removeEnzymesByEC(self, ecNumbers: Iterable[Elements.EcNumber], keepInstead = False):
        """
        Remove all enzymes associated with the passed EC numbers.
        
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Parameters
        ----------
        ecNumbers : Iterable[EcNumber]
        keepInstead : bool, optional
            If *True*, remove all enzymes except the ones associated with the passed EC numbers.
        """
        enzymesOfInterest = []
        
        for ecNumber in ecNumbers:
            foundEnzymes = self.getEnzymesForEcNumber( ecNumber )
            enzymesOfInterest.extend( foundEnzymes )
            
        enzymesOfInterest = set( enzymesOfInterest )
        
        if keepInstead == True:
            self.removeAllEnzymesExcept(enzymesOfInterest)
        else:
            self.removeEnzymes(enzymesOfInterest)
    
    def keepEnzymesByEC(self, ecNumbers: Iterable[Elements.EcNumber]):
        """
        Remove all enzymes from the graph, except the ones associated with the passed EC numbers.
        
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Parameters
        ----------
        ecNumbers : Iterable[EcNumber]
        """
        return self.removeEnzymesByEC(ecNumbers, keepInstead = True)
    


class SubstrateEcGraph(DirectedMultiGraph):
    
    def __init__(self, underlyingRawGraph: 'implementationGraph' = None):
        """
        Directed graph with :class:`Substrate` nodes and :class:`EcNumber` edges, allowing multiple edges.
            
        Links two :class:`FEV_KEGG.Graph.Elements.Substrate` (compound or glycan) nodes with each :class:`FEV_KEGG.Graph.Elements.EcNumber` edge, associated with an :class:`FEV_KEGG.Graph.Elements.Enzyme`, associated with a :class:`FEV_KEGG.Graph.Elements.GeneID`, associated with a :class:`FEV_KEGG.Graph.Elements.Reaction` they occur in.
        
        Attributes
        ----------
        self.underlyingRawGraph : :mod:`FEV_KEGG.Graph.Implementations`
            The actual graph containing the data. This is dependant on the implementation.
        self.name : str
            Custom name of the graph. This is often set, but not necessary in any calculations.
        self.substrateCounts : Dict[Substrate, int], optional
            Number of precursor graphs which contained certain :class:`Substrate` nodes still in this graph. *None* by default.
        self.ecCounts : Dict[Elements.EcNumber, int], optional
            Number of precursor graphs which contained certain :class:`EcNumber` edge keys still in this graph. *None* by default.
        """
        super().__init__(underlyingRawGraph)
    
    @property
    def substrateCounts(self):
        """
        Number of precursor graphs which contained certain :class:`Substrate` nodes still in this graph. *None* by default.
        """
        return self.nodeCounts
    
    @property
    def ecCounts(self):
        """
        Number of precursor graphs which contained certain :class:`GeneID` edge keys still in this graph. *None* by default.
        """
        return self.edgeElementCounts
    
    @staticmethod
    def fromSubstrateGeneGraph(substrateGeneGraph: SubstrateGeneGraph):
        """
        Create :class:`SubstrateEcGraph` from a :class:`SubstrateGeneGraph`.
        
        Replaces GeneIDs with their EcNumber. Splits GeneIDs with several EC numbers. Deduplicates GeneIDs with the same EC number.
        See the structure of a KEGG KGML pathway description file for further insight.
        
        Parameters
        ----------
        substrateGeneGraph : SubstrateGeneGraph
            The substrate-gene graph to use for creating this graph.
        
        Returns
        -------
        SubstrateEcGraph
            A new substrate-EC graph.
        """
        return Conversion.SubstrateGeneGraph2SubstrateEcGraph(substrateGeneGraph)
    
    @staticmethod
    def fromSubstrateEnzymeGraph(substrateEnzymeGraph: SubstrateEnzymeGraph):
        """
        Create :class:`SubstrateEcGraph` from a :class:`SubstrateEnzymeGraph`.
        
        Replaces Enzymes with their EcNumber. Splits Enzymes with several EC numbers. Deduplicates Enzymes with the same EC number.
        See the structure of a KEGG KGML pathway description file for further insight.
        
        Parameters
        ----------
        substrateEnzymeGraph : SubstrateEnzymeGraph
            The substrate-enzyme graph to use for creating this graph.
        
        Returns
        -------
        SubstrateEcGraph
            A new substrate-EC graph.
        """
        return Conversion.SubstrateEnzymeGraph2SubstrateEcGraph(substrateEnzymeGraph)
        
    def getECs(self) -> Set[Elements.EcNumber]:
        """
        Get all EC numbers.
        
        Returns
        -------
        Set[EcNumber]
            Set of all EC numbers in this graph.
        """
        return self.getEdgesElements()
    
    def addEC(self, substrate: Elements.Substrate, product: Elements.Substrate, ecNumber: Elements.EcNumber, isReversible: bool = False):
        """
        Add an `ecNumber` between the substrates `substrate` and `product`.
        
        Parameters
        ----------
        substrate : Substrate
            Automatically added, if not already in the graph.
        product : Substrate
            Automatically added, if not already in the graph.
        ecNumber : EcNumber
        isReversible : bool, optional
            If *True*, add in both directions, swapping `substrate` and `product`.
        """
        super().addEdge(substrate, product, ecNumber, isReversible) # automatically creates node, if not already present
        
    def removeECs(self, ecNumbers: Iterable[Elements.EcNumber]):
        """
        Remove all occurences of certain EC numbers.
        
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Parameters
        ----------
        ecNumbers : Iterable[EcNumber]
            Iterable of EC numbers to be completely removed from the graph.
        """
        super().removeEdgesByElement(ecNumbers)
    
    def removeAllECsExcept(self, ecToKeep: Iterable[Elements.EcNumber]):
        """
        Remove all genes which are **not** in `ecToKeep`.
        
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Parameters
        ----------
        ecToKeep : Iterable[EcNumber]
            Iterable of EC numbers to keep in the graph. All other genes are removed.
        """
        ecToKeepSet = set()
        ecToKeepSet.update(ecToKeep)
        ecToRemove = self.getECs()
        ecToRemove.difference_update(ecToKeepSet)
        self.removeECs(ecToRemove)
    
    def removeEcEdge(self, substrate: Elements.Substrate, product: Elements.Substrate, ecNumber: Elements.EcNumber, bothDirections: bool = False):
        """
        Remove a `ecNumber` between `substrate` and `product`.
        
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        
        Parameters
        ----------
        substrate : Substrate
            Not removed from the graph.
        product : Substrate
            Not removed from the graph.
        ecNumber : EcNumber
        bothDirections : bool, optional
            If *True*, remove both directions, swapping `substrate` and `product`.
        """
        super().removeEdge(substrate, product, ecNumber, bothDirections)
    
    def removeEcEdges(self, ecEdges: List[Tuple[Elements.Substrate, Elements.Substrate, Elements.EcNumber]]):
        """
        Remove all EC numbers in certain edges.
        
        Parameters
        ----------
        ecEdges : List[Tuple[Substrate, Substrate, EcNumber]]
            List of tuples, each describing an edge to be removed from the graph. If an edge to be removed does not exist, the next edge will be tried, without any error message.
        """
        for ecEdge in ecEdges:
            substrate, product, ecNumber = ecEdge
            self.removeEcEdge(substrate, product, ecNumber, bothDirections = False)
    
    def getUnidirectionalEcNumbers(self) -> Set[Elements.EcNumber]:
        """
        Get all EC numbers which have only one direction.
        
        Returns
        -------
        Set[EcNumber]
            Set of EC numbers which take part in an edge with only one direction. Meaning there is no edge with the opposite direction between the same substrated, annotated with the same gene.
        """
        return self.getUnidirectionalEdgesElements()
    
    def getPartialEcNumberEdges(self) -> List[Tuple[Elements.Substrate, Elements.Substrate, Elements.EcNumber]]:
        """
        Get all edges annotated with a partial EC number, i.e. containing a wildcard '-'.
        
        Returns
        -------
        List[Tuple[Substrate, Substrate, EcNumber]]
            List of all edge tuples where its EC number is partial, i.e. has less than the full four EC levels, e.g. '4.1.2.-'. Even though the type list does not enforce it, this should never return duplicates.
        """
        partialEdgeList = []
        edgeList = self.getEdges()
        for edge in edgeList:
            _, _, element = edge
            
            # split EC number in its four levels
            levels = element.ecNumberString.split('.')
            
            # check if there are exactly four levels
            if len(levels) != 4:
                partialEdgeList.append(edge)
                continue
            
            # check if each level is a positive integer
            for level in levels:
                if level.isdigit() == False:
                    partialEdgeList.append(edge)
                    break # prevents counting an edge multiple times if it has multiple non-integer levels
        
        return partialEdgeList
    
    def getPartialEcNumbers(self) -> Set[Elements.EcNumber]:
        """
        Get all partial EC numbers, i.e. containing a wildcard '-'.
        
        Returns
        -------
        Set[EcNumber]
            All EC numbers in this graph with less than the full four EC levels, e.g. '4.1.2.-'.
        """
        paralog_ecNumbers = set()
        edges = self.getPartialEcNumberEdges()
        for edge in edges:
            _, _, ecNumber = edge
            paralog_ecNumbers.add(ecNumber)
        
        return paralog_ecNumbers
    
    def removePartialEcNumbers(self):
        """
        Remove edges annotated with a partial EC number, i.e. containing a wildcard '-'.
        
        You may want to :func:`removeIsolatedNodes` afterwards, to remove nodes that now have no edge.
        """
        partialEdges = self.getPartialEcNumberEdges()
        super().removeEdges(partialEdges)
    











class Conversion:
    @staticmethod
    def KeggPathway2SubstrateReactionGraph(pathway: KGML_pathway.Pathway, localVerbosity = init_verbosity) -> SubstrateReactionGraph:
        """
        Converts an organism's pathway into a :class:`SubstrateReactionGraph`.
        
        Parameters
        ----------
        pathway : KGML_pathway.Pathway
        localVerbosity : int, optional
            Verbosity to be used locally. Useful to silence useless log messages. See :attr:`FEV_KEGG.settings.verbosity`.
        
        Returns
        -------
        SubstrateReactionGraph
            The substrate-reaction graph calculated from `pathway`.
        """
        # create empty graph
        graph = SubstrateReactionGraph()
        graph.pathwaySet.add(pathway)
        pathwayName = pathway.name.replace('path:', '')
        graph.name = 'Substrate-Reaction ' + pathwayName
        
        # parse reaction tags from pathway
        reactionList = pathway.reactions
        
        for reaction in reactionList:
            
            # decode a single reaction tag
            isReversible = reaction.type == 'reversible'
            substrateIDList = reaction.substrates
            productIDList = reaction.products
            reactionIDList = reaction.name.split()
            
            # build graph Elements
            substrateList = []
            productList = []
            
            # build Elements.Substrate
            for substrateID in substrateIDList:
                substrateNameList = substrateID.name.split(' ')
                for substrateNameListEntry in substrateNameList:
                    substrateName = substrateNameListEntry.split(':', 1)[1]
                    try:
                        substrate = Elements.Substrate(substrateName)
                    except Elements.DrugIdError: # ignore Drug IDs
                        continue
                    substrateList.append(substrate)
                
            for productID in productIDList:
                productNameList = productID.name.split(' ')
                for productNameListEntry in productNameList:
                    productName = productNameListEntry.split(':', 1)[1]
                    try:
                        product = Elements.Substrate(productName)
                    except Elements.DrugIdError: # ignore Drug IDs
                        continue
                    productList.append(product)
                
            # build Elements.Reaction
            for reactionID in reactionIDList:
                reactionName = reactionID.split(':', 1)[1]
                reaction = Elements.Reaction(reactionName)
                
                # fill graph with these new elements. Each substrate is connected pair-wise to every product. 
                for substrate in substrateList:
                    for product in productList:
                        graph.addReaction(substrate, product, reaction, isReversible) # automatically creates node, if not already present. In both directions, if reversible.
                        
        if localVerbosity >= 2:
            print('calculated ' + graph.name)
        
        return graph

    @classmethod
    def KeggPathwaySet2SubstrateReactionGraph(cls, pathways: Set[KGML_pathway.Pathway], localVerbosity = init_verbosity, name = None) -> SubstrateReactionGraph:
        """
        Combine several pathways of an organism into one :class:`SubstrateReactionGraph`.
        
        Deduplicates nodes and edges.
        
        Parameters
        ----------
        pathways : Set[KGML_pathway.Pathway]
        localVerbosity : int, optional
            Verbosity to be used locally. Useful to silence useless log messages. See :attr:`FEV_KEGG.settings.verbosity`.
        name : str, optional
            Name to use for the new graph.
        
        Returns
        -------
        SubstrateReactionGraph
            The substrate-reaction graph calculated from `pathways`.
        """
        newPathwaySet = set()
        #pathwayNameList = []
        graphs = []
        for pathway in pathways:
            graph = cls.KeggPathway2SubstrateReactionGraph(pathway, localVerbosity = 0)
            newPathwaySet.update(graph.pathwaySet)
            #pathwayNameList.append(pathway.name.replace('path:', ''))
            graphs.append(graph)
        
        if name is None:
            newName = 'Substrate-Reaction multiple pathways'
        else:
            newName = 'Substrate-Reaction ' + name #+ ' '.join(pathwayNameList)
        
        graph = SubstrateReactionGraph.composeAll(graphs=graphs, name=newName, pathwaySet=newPathwaySet)
        
        if localVerbosity >= 2:
            print('calculated ' + graph.name)
        
        return graph
    
    @staticmethod
    def SubstrateReactionGraph2SubstrateGeneGraph(substrateReactionGraph: SubstrateReactionGraph) -> SubstrateGeneGraph:
        """
        Convert a :class:`SubstrateReactionGraph` into a :class:`SubstrateGeneGraph`.
        
        Uses pathway information embedded into the `substrateReactionGraph`.
        
        Parameters
        ----------
        substrateReactionGraph : SubstrateReactionGraph
        
        Returns
        -------
        SubstrateGeneGraph
            The substrate-gene graph calculated from the substrate-reaction graph.
        """
        # shallow-copy old graph to new graph
        graph = SubstrateGeneGraph(substrateReactionGraph.underlyingRawGraph)
        graph.name = 'Substrate-Gene ' + substrateReactionGraph.name.split('ubstrate-Reaction ', maxsplit=1)[1]
        
        # create dict of replacements: reaction -> {genes}
        replacementDict = dict()
        
        # for each embedded pathway, get list of genes
        for pathway in substrateReactionGraph.pathwaySet:
            geneEntryList = pathway.genes
            
            # for each gene, get reactions in which it is involved
            for geneEntry in geneEntryList:
                reactionIDList = geneEntry.reaction.split()
                if len(reactionIDList) > 0: # filter genes not associated with any reaction
                    geneIDList = geneEntry.name.split()
                    
                    # replace each reaction with its associated genes
                    for reactionID in reactionIDList:
                        reactionName = reactionID.split(':', 1)[1]
                        reaction = Elements.Reaction(reactionName)
                        
                        # save associated genes in a set
                        geneSet = set()
                        for geneID in geneIDList:
                            gene = Elements.GeneID(geneID)
                            geneSet.add(gene)
                        
                        # update the replacement dict for the current reaction, adding the newly created gene set
                        replacementSet = replacementDict.get(reaction, None)
                        if replacementSet == None or replacementSet.__class__ != set:
                            replacementSet = set()
                        replacementSet.update(geneSet)
                        replacementDict[reaction] = replacementSet
        
        # get list of all reaction edges. Copy edge list to prevent changes in-place, which would NOT work
        edgeList = list(graph.getEdges())
            
        # replace reaction edges with gene edges, using replacement dict
        for edge in edgeList:
            substrate, product, reaction = edge
            
            # delete old edge
            graph.removeEdge(substrate, product, reaction, False)
            
            # add new edges, according to replacement dict
            replacementSet = replacementDict[reaction]
            for gene in replacementSet:
                graph.addGene(substrate, product, gene, False)
        
        if init_verbosity >= 2:
            print('calculated ' + graph.name)
        
        return graph
    
    @staticmethod
    def SubstrateGeneGraph2SubstrateEcGraph(substrateGeneGraph: SubstrateGeneGraph) -> SubstrateEcGraph:
        """
        Convert a :class:`SubstrateGeneGraph` into a :class:`SubstrateEcGraph`.
        
        Parameters
        ----------
        substrateGeneGraph : SubstrateGeneGraph
        
        Returns
        -------
        SubstrateEcGraph
            The substrate-EC graph calculated from the substrate-gene graph.
        
        Warnings
        --------
        Skips the substrate-enzyme step. Still parses genes from Database, this is slow and expensive!        
        """
        # shallow-copy old graph to new graph
        graph = SubstrateEcGraph(substrateGeneGraph.underlyingRawGraph)
        graph.name = 'Substrate-Ec ' + substrateGeneGraph.name.split('ubstrate-Gene ', maxsplit=1)[1]
        
        # create dict of replacements: gene -> {ec}
        replacementDict = dict()
        
        # get list of all gene edges. Copy edge list to prevent changes in-place, which would NOT work
        edgeList = list(graph.getEdges())
        
        # populate set of genes, because there are many genes used in more than one edge
        geneSet = set()
        for edge in edgeList:
            _, _, gene = edge
            geneSet.add(gene)
            
        # for each gene, retrieve ec numbers, only once per gene because this is expensive
        geneDict = Database.getGeneBulk(geneSet)
        for geneID, gene in geneDict.items():
            
            ecNumbersList = Elements.Enzyme.fromGene(gene).ecNumbers
            
            # fill replacement dict
            if ecNumbersList is not None and len(ecNumbersList) > 0:
                replacementDict[geneID] = ecNumbersList
            else:
                replacementDict[geneID] = None
                
        # replace gene edges with ec edges, using replacement dict
        for edge in edgeList:
            substrate, product, geneID = edge
            
            # delete old edge
            graph.removeEdge(substrate, product, geneID, False)
            
            # add new edges, according to replacement dict
            replacementList = replacementDict[geneID]
            if replacementList is not None:
                for ecNumber in replacementList:
                    graph.addEC(substrate, product, ecNumber, False)
        
        if init_verbosity >= 2:
            print('calculated ' + graph.name)
        
        return graph
    
    @staticmethod
    def SubstrateGeneGraph2SubstrateEnzymeGraph(substrateGeneGraph: SubstrateGeneGraph, noMultifunctional = False) -> SubstrateEnzymeGraph:
        """
        Convert a :class:`SubstrateGeneGraph` into a :class:`SubstrateEnzymeGraph`.
        
        Each unique gene ID is mapped to the same unique enzyme, because enzymes are unique by their gene ID.
        
        Parameters
        ----------
        substrateGeneGraph : SubstrateGeneGraph
        
        Returns
        -------
        SubstrateEnzymeGraph
            The substrate-enzyme graph calculated from the substrate-gene graph.
        
        Warnings
        --------
        Parses genes from Database, this is slow and expensive!
        """
        # shallow-copy old graph to new graph
        graph = SubstrateEnzymeGraph(substrateGeneGraph.underlyingRawGraph)
        graph.name = 'Substrate-Enzyme ' + substrateGeneGraph.name.split('ubstrate-Gene ', maxsplit=1)[1]
        
        # create dict of replacements: gene -> enzyme
        replacementDict = dict()
        
        # get list of all gene edges. Copy edge list to prevent changes in-place, which would NOT work
        edgeList = list(graph.getEdges())
        
        # populate set of genes, because there are many genes used in more than one edge
        geneSet = set()
        for edge in edgeList:
            _, _, gene = edge
            geneSet.add(gene)
            
        # for each gene, build enzyme object, only once per gene because this is expensive
        geneDict = Database.getGeneBulk(geneSet)
        for geneID, gene in geneDict.items():

            enzyme = Elements.Enzyme.fromGene(gene)
        
            # fill replacement dict
            if enzyme is not None:
                if noMultifunctional is True: # if required, ignore enzymes with multiple EC numbers
                    if len(enzyme.ecNumbers) > 1:
                        continue
                replacementDict[geneID] = enzyme
                
        # replace gene edges with enzyme edges, using replacement dict
        for edge in edgeList:
            substrate, product, geneID = edge
            
            # delete old edge
            graph.removeEdge(substrate, product, geneID, False)
            
            # add new edges, according to replacement dict
            enzyme = replacementDict.get(geneID, None)
            if enzyme is not None:
                graph.addEnzyme(substrate, product, enzyme, False)
        
        if init_verbosity >= 2:
            print('calculated ' + graph.name)
        
        return graph
        
    @staticmethod
    def SubstrateEnzymeGraph2SubstrateEcGraph(substrateEnzymeGraph: SubstrateEnzymeGraph) -> SubstrateEcGraph:
        """
        Convert a :class:`SubstrateEnzymeGraph` into a :class:`SubstrateEcGraph`.
        
        Parameters
        ----------
        substrateEnzymeGraph : SubstrateEnzymeGraph
        
        Returns
        -------
        SubstrateEcGraph
            The substrate-EC graph calculated from the substrate-enzyme graph.
        """        
        # shallow-copy old graph to new graph
        graph = SubstrateEcGraph(substrateEnzymeGraph.underlyingRawGraph)
        graph.name = 'Substrate-Ec ' + substrateEnzymeGraph.name.split('ubstrate-Enzyme ', maxsplit=1)[1]
        
        # get list of all enzyme edges. Copy edge list to prevent changes in-place, which would NOT work
        edgeList = list(graph.getEdges())
        
        # replace enzyme edges with ec edges, duplicates will be ignored
        for edge in edgeList:
            substrate, product, enzyme = edge
            
            # delete old edge
            graph.removeEdge(substrate, product, enzyme, False)
            
            # add new edges
            replacementList = enzyme.ecNumbers
            if replacementList is not None:
                for ecNumber in replacementList:
                    graph.addEC(substrate, product, ecNumber, False)
        
        if init_verbosity >= 2:
            print('calculated ' + graph.name)
        
        return graph
