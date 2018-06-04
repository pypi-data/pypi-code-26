from FEV_KEGG.Graph.SubstrateGraphs import SubstrateEcGraph, SubstrateEnzymeGraph
from FEV_KEGG.Evolution.Taxonomy import NCBI, Taxonomy
from FEV_KEGG.KEGG.Organism import Group 
from FEV_KEGG.Graph.Elements import EcNumber, Enzyme
from typing import Set, Tuple
from FEV_KEGG.Evolution.Events import GeneFunctionAddition, GeneFunctionLoss, GeneFunctionDivergence, GeneFunctionConservation,\
    MajorityNeofunctionalisation, SimpleGeneDuplication
from FEV_KEGG import settings
from builtins import str
from FEV_KEGG.Drawing import Export

defaultExcludeUnclassified = True
"""
If *True*, ignore taxons with a path containing the string 'unclassified'.
This can be overridden in each relevant method's `excludeUnclassified` parameter in this module.
"""
defaultExcludeMultifunctionalEnzymes = True
"""
If *True*, ignore enzymes with more than one EC number.
This can be overridden in each relevant method's `excludeMultifunctionalEnzymes` parameter in this module.
"""
defaultMajorityPercentageCoreMetabolism = 80
"""
Default percentage of organisms in the clade, which have to possess an EC number, for it to be included in the core metabolism of the clade.
See :func:`FEV_KEGG.KEGG.Organism.Group.majorityEcGraph`.
This can be overridden in each relevant method's `majorityPercentageCoreMetabolism` parameter in this module.
"""
defaultMajorityPercentageGeneDuplication = 70
"""
Default percentage of organisms in the clade, which have to possess the same neofunctionalised EC number, for it to be included in the set of neofunctionalised EC numbers of the clade.
See :func:`FEV_KEGG.KEGG.Evolution.Events.getEnzymesForEC`.
This can be overridden in each relevant method's `majorityPercentageGeneDuplication` parameter in this module.
"""
defaultEValue = settings.defaultEvalue
"""
Default threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
"""

class Clade(object):
    
    def __init__(self, ncbiNames: 'e.g. Enterobacter or Proteobacteria/Gammaproteobacteria. Allows list of names, e.g. ["Gammaproteobacteria", "/Archaea"]', excludeUnclassified = defaultExcludeUnclassified):
        """
        A clade in NCBI taxonomy, containing all leaf taxon's KEGG organisms.
        
        Parameters
        ----------
        ncbiNames : str or Iterable[str]
            String(s) a taxon's path must contain to be included in this clade.
        excludeUnclassified : bool, optional
            If *True*, ignore taxons with a path containing the string 'unclassified'.
        
        Attributes
        ----------
        self.ncbiNames : Iterable[str]
            Part of the path of each leaf taxon to be included in this clade. A single string is wrapped in a list.
        self.group
            The :class:`FEV_KEGG.KEGG.Organism.Group` of KEGG organisms created from the found leaf taxons.
        
        Raises
        ------
        ValueError
            If no clade with `ncbiNames` in its path could be found.
        
        Warnings
        --------
        It is possible to include organisms of several clades in the same Clade object!
        For example, if you were to search for `ncbiNames` == 'Donaldus Duckus', you would get every organism within '/Bacteria/Donaldus Duckus' **and** '/Archaea/Order/Donaldus Duckus'.
        Use the slash (/) notation to make sure you only get the taxon you want, e.g. 'Proteobacteria/Gammaproteobacteria' or '/Archaea'.
        """
        taxonomy = NCBI.getTaxonomy()
        
        if isinstance(ncbiNames, str):
            ncbiNames = [ncbiNames]
            
        self.ncbiNames = ncbiNames
        
        allOrganisms = set()
        for ncbiName in ncbiNames:
            organisms = taxonomy.getOrganismAbbreviationsByPath(ncbiName, exceptPaths=('unclassified' if excludeUnclassified else None))
            if organisms is None or len(organisms) == 0:
                raise ValueError("No clade of this path found: " + ncbiName)
            allOrganisms.update(organisms)
        
        self.group = Group( allOrganisms )
    
    def collectiveMetabolism(self, excludeMultifunctionalEnzymes = defaultExcludeMultifunctionalEnzymes) -> SubstrateEcGraph:
        """
        The Substrate-EC graph representing the collective metabolic network, occuring in any organism of the clade.
        
        This includes each and every EC number which occurs in any organism of this clade.
        
        Parameters
        ----------
        excludeMultifunctionalEnzymes : bool, optional
            If *True*, ignore enzymes with more than one EC number.
        
        Returns
        -------
        SubstrateEcGraph
            Collective metabolic network of EC numbers, including counts of occurence in each of the clade's organisms.
        
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails.
        """
        graph = self.group.collectiveEcGraph(noMultifunctional = excludeMultifunctionalEnzymes, addCount = True, keepOnHeap = True)
        graph.name = 'Collective metabolism ECs ' + ' '.join(self.ncbiNames)
        return graph
    
    def collectiveMetabolismEnzymes(self, excludeMultifunctionalEnzymes = defaultExcludeMultifunctionalEnzymes) -> SubstrateEnzymeGraph:
        """
        The Substrate-Enzyme graph representing the collective metabolic network, occuring in any organism of the clade.
        
        This includes each and every enzyme of every organism of this clade.
        
        Parameters
        ----------
        excludeMultifunctionalEnzymes : bool, optional
            If *True*, ignore enzymes with more than one EC number.
        
        Returns
        -------
        SubstrateEnzymeGraph
            Collective metabolic network of enzymes.
        
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails.
        """
        graph = self.group.collectiveEnzymeGraph(noMultifunctional = excludeMultifunctionalEnzymes, keepOnHeap = True)
        graph.name = 'Collective metabolism enzymes ' + ' '.join(self.ncbiNames)
        return graph
    
    def coreMetabolism(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism, excludeMultifunctionalEnzymes = defaultExcludeMultifunctionalEnzymes) -> SubstrateEcGraph:
        """
        The Substrate-EC graph representing the common metabolic network, shared among all organisms of the clade.
        
        This includes only EC numbers which occur in at least `majorityPercentageCoreMetabolism` % of all organisms of this clade.
        
        Parameters
        ----------
        majorityPercentageCoreMetabolism : int, optional
            A path (substrate -> EC -> product) has to occur in `majorityPercentageCoreMetabolism` % of the clade's organisms to be included.
        excludeMultifunctionalEnzymes : bool, optional
            If *True*, ignore enzymes with more than one EC number.
        
        Returns
        -------
        SubstrateEcGraph
            Core metabolic network of EC numbers.
        
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails.
        """
        graph = self.group.majorityEcGraph(majorityPercentage = majorityPercentageCoreMetabolism, noMultifunctional = excludeMultifunctionalEnzymes, keepOnHeap = True)
        graph.name = 'Core metabolism ECs ' + ' '.join(self.ncbiNames)
        return graph
    
    def coreMetabolismEnzymes(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism, excludeMultifunctionalEnzymes = defaultExcludeMultifunctionalEnzymes) -> SubstrateEnzymeGraph:
        """
        The Substrate-Enzyme graph representing the common metabolic network, shared among all organisms of the clade.
        
        This includes every Enzyme associated with an EC number occuring in core metabolism (see :func:`coreMetabolism`), no matter from which organism it stems.
        
        Parameters
        ----------
        majorityPercentageCoreMetabolism : int, optional
            A path (substrate -> EC -> product) has to occur in `majorityPercentageCoreMetabolism` % of the clade's organisms to be included.
        excludeMultifunctionalEnzymes : bool, optional
            If *True*, ignore enzymes with more than one EC number.
        
        Returns
        -------
        SubstrateEnzymeGraph
            Core metabolic network of enzymes.
        
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails.
        """
        graph = self.group.collectiveEnzymeGraphByEcMajority(majorityPercentage = majorityPercentageCoreMetabolism, majorityTotal = None, noMultifunctional = excludeMultifunctionalEnzymes)
        graph.name = 'Core metabolism Enzymes ' + ' '.join(self.ncbiNames)
        return graph
    
    @property
    def organismsCount(self) -> int:
        """
        The number of organisms (leaf taxons) in this clade.
        
        Returns
        -------
        int
            The number of organisms (leaf taxons) in this clade.
        """
        return self.group.organismsCount


class CladePair(object):
    
    def __init__(self, parent, child, excludeUnclassified = defaultExcludeUnclassified):
        """
        Two clades in NCBI taxonomy, 'child' is assumed younger than 'parent'.
        
        Does not check if the child taxon is actually a child of the parent taxon.
        Therefore, it would be possible to pass a list of NCBI names to the underlying :class:`Clade` objects by instantiating `parent` = List[str] and/or `child` = List[str].
        This is useful when comparing groups of organisms which are, according to NCBI, not related.
        
        Parameters
        ----------
        parent : str or List[str] or Clade
            Path(s) of the parent clade's taxon, as defined by NCBI taxonomy, e.g. 'Proteobacteria/Gammaproteobacteria'. Or a ready :class:`Clade` object.
        child : str or List[str] or Clade
            Path(s) of the child clade's taxon, as defined by NCBI taxonomy, e.g. 'Enterobacter'. Or a ready :class:`Clade` object.
        excludeUnclassified : bool, optional
            If *True*, ignore taxons with a path containing the string 'unclassified'.
        
        Attributes
        ----------
        self.childClade : :class:`Clade`
        self.parentClade : :class:`Clade`
        """
        # read NCBI names from Clade object, if necessary
        if isinstance(parent, Clade):
            self.parentClade = parent
        else:
            self.parentClade = Clade(parent, excludeUnclassified)
        
        if isinstance(child, Clade):
            self.childClade = child
        else:
            self.childClade = Clade(child, excludeUnclassified)
    
    
    @property
    def parentNCBInames(self):
        """
        All names/paths in NCBI taxonomy used to create the parent clade.
        """
        return self.parentClade.ncbiNames
    
    @property
    def childNCBInames(self):
        """
        All names/paths in NCBI taxonomy used to create the child clade.
        """
        return self.childClade.ncbiNames
    
    
    def conservedMetabolism(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism) -> SubstrateEcGraph:
        """
        Substrate-EC graph of the conserved core metabolism.
        
        Parameters
        ----------
        majorityPercentageCoreMetabolism : int, optional
            Every substrate-EC-product edge has to occur in `majorityPercentageCoreMetabolism` % of organisms constituting the clade, to be included in the core metabolism. This is individually true for both parent clade and child clade.
            The parent clade fully includes the child clade, therefore, the occurence of a substrate-EC-product edge in the child clade's core metabolism counts towards the percentage for the parent clade's core metabolism.
            Meaning: if an EC number does not occur in the child clade's core metabolism, it is unlikely that it will occur in the parent clade's core metabolism, unless `majorityPercentageCoreMetabolism` is consecutively lowered towards 0.
        
        Returns
        -------
        SubstrateEcGraph
            The substrate-EC graph representing the metabolic network which stayed the same between the core metabolism of the parent (assumed older) and the core metabolism of the child (assumed younger).
            
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        graph = GeneFunctionConservation.getGraph(parentCoreMetabolism, childCoreMetabolism)
        graph.name = 'Conserved metabolism ' + ' '.join(self.parentNCBInames) + ' -> ' + ' '.join(self.childNCBInames)
        return graph
    
    def conservedMetabolismEnzymes(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism, colour = False):
        """
        Two Substrate-Enzyme graphs derived from the conserved core metabolism, see :func:`conservedMetabolism`.
        
        First, the conserved core metabolism is calculated. Then, the enzymes associated with the conserved EC numbers are extracted from the collective parent's and child's metabolism individually.
        
        Parameters
        ----------
        majorityPercentageCoreMetabolism : int, optional
            See :func:`conservedMetabolism`.
        colour : bool, optional
            If *True*, colours the enzyme edges from the parent in blue, and from the child in red. When doing so, a single :class:`SubstrateEnzymeGraph` is returned, not a :class:`Tuple`. The colouring is realised by adding a 'colour' attribute to each edge. Nodes are not coloured.
        
        Returns
        -------
        Tuple[SubstrateEnzymeGraph, SubstrateEnzymeGraph] or SubstrateEnzymeGraph
            Tuple of two Substrate-Enzyme graphs calculated using the conserved EC numbers found by :func:`conservedMetabolism`. The first graph is from the parent clade, the second graph from the child clade.
            If `colour` == *True*, returns a single Substrate-Enzyme graph, coloured blue for parent and red for child.
        
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        conservedECs = GeneFunctionConservation.getECs(parentCoreMetabolism, childCoreMetabolism)
        
        parentGraph = self.parentClade.collectiveMetabolismEnzymes().keepEnzymesByEC(conservedECs)        
        childGraph = self.childClade.collectiveMetabolismEnzymes().keepEnzymesByEC(conservedECs)    
    
        if colour is True:
            parentEdges = parentGraph.getEdges()
            childEdges = childGraph.getEdges()
            
            graph = parentGraph.union(childGraph, addCount = False, updateName = False)
            
            Export.addColourAttribute(graph, colour = Export.Colour.BLUE, nodes = False, edges = parentEdges)
            Export.addColourAttribute(graph, colour = Export.Colour.RED, nodes = False, edges = childEdges)
            
            graph.name = 'Conserved metabolism enzymes ' + ' '.join(self.parentNCBInames) + ' -> ' + ' '.join(self.childNCBInames)
            
            return graph
        else:
            parentGraph.name = 'Conserved metabolism enzymes *' + ' '.join(self.parentNCBInames) + '* -> ' + ' '.join(self.childNCBInames)
            childGraph.name = 'Conserved metabolism enzymes ' + ' '.join(self.parentNCBInames) + ' -> *' + ' '.join(self.childNCBInames) + '*'
        
            return (parentGraph, childGraph)
    
    
    def addedMetabolism(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism) -> SubstrateEcGraph:
        """
        Substrate-EC graph of the added core metabolism.
        
        Parameters
        ----------
        majorityPercentageCoreMetabolism : int, optional
            Every substrate-EC-product edge has to occur in `majorityPercentageCoreMetabolism` % of organisms constituting the clade, to be included in the core metabolism. This is individually true for both parent clade and child clade.
            The parent clade fully includes the child clade, therefore, the occurence of a substrate-EC-product edge in the child clade's core metabolism counts towards the percentage for the parent clade's core metabolism.
            Meaning: if an EC number does not occur in the child clade's core metabolism, it is unlikely that it will occur in the parent clade's core metabolism, unless `majorityPercentageCoreMetabolism` is consecutively lowered towards 0.
        
        Returns
        -------
        SubstrateEcGraph
            The substrate-EC graph representing the metabolic network which was added to the core metabolism of the parent (assumed older) on the way to the core metabolism of the child (assumed younger).
            
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        graph = GeneFunctionAddition.getGraph(parentCoreMetabolism, childCoreMetabolism)
        graph.name = 'Added metabolism ' + ' '.join(self.parentNCBInames) + ' -> ' + ' '.join(self.childNCBInames)
        return graph
    
    def addedMetabolismEnzymes(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism) -> SubstrateEnzymeGraph:
        """
        Substrate-Enzyme graph derived from the added core metabolism, see :func:`addedMetabolism`.
        
        First, the added core metabolism is calculated. Then, the enzymes associated with the added EC numbers are extracted from the child's enzyme metabolism.
        
        Parameters
        ----------
        majorityPercentageCoreMetabolism : int, optional
            See :func:`addedMetabolism`.
        
        Returns
        -------
        SubstrateEnzymeGraph
            Substrate-Enzyme graph of enzymes from the child clade. Calculated using the added EC numbers found by :func:`addedMetabolism`.
        
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        addedECs = GeneFunctionAddition.getECs(parentCoreMetabolism, childCoreMetabolism)
        
        childGraph = self.childClade.collectiveMetabolismEnzymes().keepEnzymesByEC(addedECs)
        childGraph.name = 'Added metabolism enzymes ' + ' '.join(self.parentNCBInames) + ' -> ' + ' '.join(self.childNCBInames)
        
        return childGraph
    
    
    def lostMetabolism(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism) -> SubstrateEcGraph:
        """
        Substrate-EC graph of the lost core metabolism.
        
        Parameters
        ----------
        majorityPercentageCoreMetabolism : int, optional
            Every substrate-EC-product edge has to occur in `majorityPercentageCoreMetabolism` % of organisms constituting the clade, to be included in the core metabolism. This is individually true for both parent clade and child clade.
            The parent clade fully includes the child clade, therefore, the occurence of a substrate-EC-product edge in the child clade's core metabolism counts towards the percentage for the parent clade's core metabolism.
            Meaning: if an EC number does not occur in the child clade's core metabolism, it is unlikely that it will occur in the parent clade's core metabolism, unless `majorityPercentageCoreMetabolism` is consecutively lowered towards 0.
        
        Returns
        -------
        SubstrateEcGraph
            The substrate-EC graph representing the metabolic network which got lost from the core metabolism of the parent (assumed older) on the way to the core metabolism of the child (assumed younger).
            
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)        
        graph = GeneFunctionLoss.getGraph(parentCoreMetabolism, childCoreMetabolism)
        graph.name = 'Lost metabolism ' + ' '.join(self.parentNCBInames) + ' -> ' + ' '.join(self.childNCBInames)
        return graph
    
    def lostMetabolismEnzymes(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism) -> SubstrateEnzymeGraph:
        """
        Substrate-Enzyme graph derived from the lost core metabolism, see :func:`lostMetabolism`.
        
        First, the lost core metabolism is calculated. Then, the enzymes associated with the added EC numbers are extracted from the parent's enzyme metabolism.
        
        Parameters
        ----------
        majorityPercentageCoreMetabolism : int, optional
            See :func:`lostMetabolism`.
        
        Returns
        -------
        SubstrateEnzymeGraph
            Substrate-Enzyme graph of enzymes from the parent clade. Calculated using the lost EC numbers found by :func:`lostMetabolism`.
        
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        lostECs = GeneFunctionLoss.getECs(parentCoreMetabolism, childCoreMetabolism)
        
        parentGraph = self.parentClade.collectiveMetabolismEnzymes().keepEnzymesByEC(lostECs)
        parentGraph.name = 'Lost metabolism enzymes ' + ' '.join(self.parentNCBInames) + ' -> ' + ' '.join(self.childNCBInames)
        
        return parentGraph
    
    
    def divergedMetabolism(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism, colour = False) -> SubstrateEcGraph:
        """
        Substrate-EC graph of the diverged core metabolism.
        
        Parameters
        ----------
        majorityPercentageCoreMetabolism : int, optional
            Every substrate-EC-product edge has to occur in `majorityPercentageCoreMetabolism` % of organisms constituting the clade, to be included in the core metabolism. This is individually true for both parent clade and child clade.
            The parent clade fully includes the child clade, therefore, the occurence of a substrate-EC-product edge in the child clade's core metabolism counts towards the percentage for the parent clade's core metabolism.
            Meaning: if an EC number does not occur in the child clade's core metabolism, it is unlikely that it will occur in the parent clade's core metabolism, unless `majorityPercentageCoreMetabolism` is consecutively lowered towards 0.
        colour : bool, optional
            If *True*, colours the lost EC edges in blue, and the added EC edges in red. The colouring is realised by adding a 'colour' attribute to each edge. Nodes are not coloured.
        
        Returns
        -------
        SubstrateEcGraph
            The substrate-EC graph representing the metabolic network which changed between the core metabolism of the parent (assumed older) and the core metabolism of the child (assumed younger).
            
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        
        if colour is True:
            lostGraph = GeneFunctionLoss.getGraph(parentCoreMetabolism, childCoreMetabolism)
            lostEdges = lostGraph.getEdges()
            
            addedGraph = GeneFunctionAddition.getGraph(parentCoreMetabolism, childCoreMetabolism)
            addedEdges = addedGraph.getEdges()
            
            graph = lostGraph.union(addedGraph, addCount = False, updateName = False) 
            
            Export.addColourAttribute(graph, colour = Export.Colour.BLUE, nodes = False, edges = lostEdges)
            Export.addColourAttribute(graph, colour = Export.Colour.RED, nodes = False, edges = addedEdges)
            
        else:       
            graph = GeneFunctionDivergence.getGraph(parentCoreMetabolism, childCoreMetabolism)
        
        graph.name = 'Diverged metabolism ' + ' '.join(self.parentNCBInames) + ' -> ' + ' '.join(self.childNCBInames)
            
        return graph
    
    def divergedMetabolismEnzymes(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism, colour = False):
        """
        Two Substrate-Enzyme graphs derived from the diverged core metabolism, see :func:`divergedMetabolism`.
        
        First, the diverged core metabolism is calculated. Then, the enzymes associated with the added EC numbers are extracted from the collective parent's and child's metabolism individually.
        
        Parameters
        ----------
        majorityPercentageCoreMetabolism : int, optional
            See :func:`divergedMetabolism`.
        colour : bool, optional
            If *True*, colours the lost enzyme edges in blue, and the added enzyme edges in red. When doing so, a single :class:`SubstrateEnzymeGraph` is returned, not a :class:`Tuple`. The colouring is realised by adding a 'colour' attribute to each edge. Nodes are not coloured.
        
        Returns
        -------
        Tuple[SubstrateEnzymeGraph, SubstrateEnzymeGraph] or SubstrateEnzymeGraph
            Tuple of two Substrate-Enzyme graphs calculated using the diverged EC numbers found by :func:`divergedMetabolism`. The first graph is from the parent clade, the second graph from the child clade.
            If `colour` == *True*, returns a single Substrate-Enzyme graph, coloured blue for parent and red for child.
        
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        divergedECs = GeneFunctionDivergence.getECs(parentCoreMetabolism, childCoreMetabolism)
        
        parentGraph = self.parentClade.collectiveMetabolismEnzymes().keepEnzymesByEC(divergedECs)        
        childGraph = self.childClade.collectiveMetabolismEnzymes().keepEnzymesByEC(divergedECs)
        
        if colour is True:
            parentEdges = parentGraph.getEdges()
            childEdges = childGraph.getEdges()
            
            graph = parentGraph.union(childGraph, addCount = False, updateName = False)
            
            Export.addColourAttribute(graph, colour = Export.Colour.BLUE, nodes = False, edges = parentEdges)
            Export.addColourAttribute(graph, colour = Export.Colour.RED, nodes = False, edges = childEdges)
            
            graph.name = 'Diverged metabolism enzymes ' + ' '.join(self.parentNCBInames) + ' -> ' + ' '.join(self.childNCBInames)
            
            return graph
        else:
            parentGraph.name = 'Diverged metabolism enzymes *' + ' '.join(self.parentNCBInames) + '* -> ' + ' '.join(self.childNCBInames)
            childGraph.name = 'Diverged metabolism enzymes ' + ' '.join(self.parentNCBInames) + ' -> *' + ' '.join(self.childNCBInames) + '*'
        
            return (parentGraph, childGraph)
    
    
    def unifiedMetabolism(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism, colour = False) -> SubstrateEcGraph:
        """
        Substrate-EC graph of the unified core metabolisms.
        
        The lost metabolism of the parent is coloured in blue, the conserved metabolism of both in red, and the added metabolism of the child in pink.
        The colouring is realised by adding a 'colour' attribute to each edge. Nodes are not coloured.
        
        Parameters
        ----------
        majorityPercentageCoreMetabolism : int, optional
            See :func:`conservedMetabolism`.
        colour : bool, optional
            If *True*, colours the parent's EC edges in blue, the child's EC edges in red, and the shared EC edges in pink. The colouring is realised by adding a 'colour' attribute to each edge. Nodes are not coloured.
        
        Returns
        -------
        SubstrateEcGraph
            The substrate-EC graph representing the combined metabolic networks of both, child and parent. If `colour` == *True*, coloured differently for the lost, conserved, and added edges. Nodes are not coloured.
        
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails.
        
        See Also
        --------
        :mod:`FEV_KEGG.Drawing.Export` : Export the graph into a file, e.g. for visualisation in Cytoscape.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        
        graph = parentCoreMetabolism.union(childCoreMetabolism, addCount = False, updateName = False)
        graph.name = 'Unified metabolism ' + ' '.join(self.parentNCBInames) + ' -> ' + ' '.join(self.childNCBInames)
        
        if colour is True:
            lostGraph = GeneFunctionLoss.getGraph(parentCoreMetabolism, childCoreMetabolism)
            lostEdges = lostGraph.getEdges()
            
            addedGraph = GeneFunctionAddition.getGraph(parentCoreMetabolism, childCoreMetabolism)
            addedEdges = addedGraph.getEdges()
            
            conservedGraph = GeneFunctionConservation.getGraph(parentCoreMetabolism, childCoreMetabolism)
            conservedEdges = conservedGraph.getEdges()            
            
            Export.addColourAttribute(graph, colour = Export.Colour.BLUE, nodes = False, edges = lostEdges)
            Export.addColourAttribute(graph, colour = Export.Colour.RED, nodes = False, edges = addedEdges)
            Export.addColourAttribute(graph, colour = Export.Colour.PINK, nodes = False, edges = conservedEdges)        
            
        return graph
    
    
    def unifiedMetabolismEnzymes(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism, colour = False) -> SubstrateEnzymeGraph:
        """
        Substrate-EC graph of the unified core metabolisms.
        
        The lost metabolism of the parent is coloured in blue, the conserved metabolism of both in red, and the added metabolism of the child in pink.
        The colouring is realised by adding a 'colour' attribute to each edge. Nodes are not coloured.
        
        Parameters
        ----------
        majorityPercentageCoreMetabolism : int, optional
            See :func:`conservedMetabolism`.
        colour : bool, optional
            If *True*, colours the parent's enzyme edges in blue, and the child's enzyme edges in red. The colouring is realised by adding a 'colour' attribute to each edge. Nodes are not coloured.
        
        Returns
        -------
        SubstrateEcGraph
            The substrate-EC graph representing the combined metabolic networks of both, child and parent. If `colour` == *True*, coloured differently for the lost, conserved, and added edges. Nodes are not coloured.
        
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails.
        """
        parentGraph = self.parentClade.coreMetabolismEnzymes(majorityPercentageCoreMetabolism)
        childGraph = self.childClade.coreMetabolismEnzymes(majorityPercentageCoreMetabolism)
        
        graph = parentGraph.union(childGraph, addCount = False, updateName = False)
        graph.name = 'Diverged metabolism enzymes ' + ' '.join(self.parentNCBInames) + ' -> ' + ' '.join(self.childNCBInames)
        
        if colour is True:
            parentEdges = parentGraph.getEdges()
            childEdges = childGraph.getEdges()
            
            Export.addColourAttribute(graph, colour = Export.Colour.BLUE, nodes = False, edges = parentEdges)
            Export.addColourAttribute(graph, colour = Export.Colour.RED, nodes = False, edges = childEdges)
            
            return graph
                
        return graph

    
    
    
    
    def neofunctionalisedMetabolism(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism, majorityPercentageGeneDuplication = defaultMajorityPercentageGeneDuplication, colour = False) -> SubstrateEcGraph:
        """
        The substrate-EC graph of EC numbers belonging to neofunctionalised enzymes.
        
        First calculates :func:`addedMetabolism`, then filters results for gene duplication.
        The maximum expectation value (e-value) necessary for a sequence alignment to constitute a "similar sequence" can be changed via :attr:`defaultEValue`.
        
        Parameters
        ----------
        majorityPercentageCoreMetabolism : int, optional
            Every substrate-EC-product edge has to occur in `majorityPercentageCoreMetabolism` % of organisms constituting the clade, to be included in the core metabolism. This is individually true for both parent clade and child clade.
            The parent clade fully includes the child clade, therefore, the occurence of a substrate-EC-product edge in the child clade's core metabolism counts towards the percentage for the parent clade's core metabolism.
            Meaning: if an EC number does not occur in the child clade's core metabolism, it is unlikely that it will occur in the parent clade's core metabolism, unless `majorityPercentageCoreMetabolism` is consecutively lowered towards 0.
        majorityPercentageGeneDuplication : int, optional
            Every EC number considered for neofunctionalisation has to be associated with enzymes which fulfil the conditions of gene duplication in at least `majorityPercentageGeneDuplication` % of child clade's organisms.
            A high `majorityPercentageGeneDuplication` disallows us to detect neofunctionalisations which happened a long time ago, with their genes having diverged significantly; 
            or only recently, with not all organisms of the child clade having picked up the new function, yet.
            However, it also enables us to practically exclude horizontal gene transfer; IF the transferred gene did not already have a sister gene in the receiving organism, with a similar sequence, creating a false positive for gene duplication.
        colour : bool, optional
            If *True*, colours the parent's EC edges in blue, the child's EC edges in red, the shared EC edges in pink, and the neofunctionalised EC edges in green. The colouring is realised by adding a 'colour' attribute to each edge. Nodes are not coloured.
        
        Returns
        -------
        SubstrateEcGraph
            The substrate-EC graph representing the metabolic network which was neofunctionalised between the core metabolism of the parent (assumed older) and the core metabolism of the child (assumed younger), and nothing else.
            If `colour` == *True*, returns the full union of parent and child, colouring neofunctionalised ECs green.
        
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails. 
        """
        descendantEnzymeGraph = self.childClade.coreMetabolismEnzymes(majorityPercentageCoreMetabolism)
        geneDuplicationModel = SimpleGeneDuplication
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        newECs = GeneFunctionAddition.getECs(parentCoreMetabolism, childCoreMetabolism)
        neofunctionalisedMetabolism = MajorityNeofunctionalisation.filterECs(childCoreMetabolism, descendantEnzymeGraph, geneDuplicationModel, newECs, self.childClade.organismsCount,  majorityPercentage = majorityPercentageGeneDuplication, eValue = defaultEValue)
        
        if colour is True:
            neofunctionalisedMetabolismOnly = neofunctionalisedMetabolism
            neofunctionalisedMetabolism = self.unifiedMetabolism(majorityPercentageCoreMetabolism = majorityPercentageCoreMetabolism, colour = True)
            Export.addColourAttribute(neofunctionalisedMetabolism, Export.Colour.GREEN, nodes = False, edges = neofunctionalisedMetabolismOnly.getEdges())
        
        neofunctionalisedMetabolism.name = 'Neofunctionalised metabolism ' + ' '.join(self.parentNCBInames) + ' -> ' + ' '.join(self.childNCBInames)
        
        return neofunctionalisedMetabolism
        
    def neofunctionalisedMetabolismSet(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism, majorityPercentageGeneDuplication = defaultMajorityPercentageGeneDuplication) -> Set[EcNumber]:
        """
        Same as :func:`neofunctionalisedMetabolism` . :func:`getECs`, but faster.
        """
        descendantEnzymeGraph = self.childClade.coreMetabolismEnzymes(majorityPercentageCoreMetabolism)
        geneDuplicationModel = SimpleGeneDuplication
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        newECs = GeneFunctionAddition.getECs(parentCoreMetabolism, childCoreMetabolism)
        neofunctionalisedECs = MajorityNeofunctionalisation.getECs(descendantEnzymeGraph, geneDuplicationModel, newECs, self.childClade.organismsCount,  majorityPercentage = majorityPercentageGeneDuplication, eValue = defaultEValue)
        return neofunctionalisedECs
    
    
    def neofunctionalisedMetabolismEnzymes(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism, majorityPercentageGeneDuplication = defaultMajorityPercentageGeneDuplication, colour = False) -> SubstrateEnzymeGraph:
        """
        The substrate-Enzyme graph in accordance with :func:`neofunctionalisedMetabolism`.
        
        First, the neofunctionalised core metabolism is calculated. Then, the enzymes associated with the neofunctionalised EC numbers are extracted from the child's core metabolism.
        
        Parameters
        ----------
        majorityPercentageCoreMetabolism : int, optional
            Every substrate-EC-product edge has to occur in `majorityPercentageCoreMetabolism` % of organisms constituting the clade, to be included in the core metabolism. This is individually true for both parent clade and child clade.
            The parent clade fully includes the child clade, therefore, the occurence of a substrate-EC-product edge in the child clade's core metabolism counts towards the percentage for the parent clade's core metabolism.
            Meaning: if an EC number does not occur in the child clade's core metabolism, it is unlikely that it will occur in the parent clade's core metabolism, unless `majorityPercentageCoreMetabolism` is consecutively lowered towards 0.
        majorityPercentageGeneDuplication : int, optional
            Every EC number considered for neofunctionalisation has to be associated with enzymes which fulfil the conditions of gene duplication in at least `majorityPercentageGeneDuplication` % of child clade's organisms.
            A high `majorityPercentageGeneDuplication` disallows us to detect neofunctionalisations which happened a long time ago, with their genes having diverged significantly; 
            or only recently, with not all organisms of the child clade having picked up the new function, yet.
            However, it also enables us to practically exclude horizontal gene transfer; IF the transferred gene did not already have a sister gene in the receiving organism, with a similar sequence, creating a false positive for gene duplication.
        colour : bool, optional
            If *True*, colours the parent's enzyme edges in blue, the child's enzyme edges in red, and the neofunctionalised enzyme edges in green. The colouring is realised by adding a 'colour' attribute to each edge. Nodes are not coloured.
        
        Returns
        -------
        SubstrateEnzymeGraph
            Substrate-Enzyme graph containing all neofunctionalised enzymes, and nothing else. If `colour` == *True*, returns the full union of parent and child, colouring neofunctionalised enzymes green.
        
        Raises
        ------
        TypeError
            If you failed to enable :attr:`FEV_KEGG.settings.automaticallyStartProcessPool` or to provide a :attr:`FEV_KEGG.Util.Parallelism.processPool`. See :func:`FEV_KEGG.KEGG.Organism.Group._getGraphsParallelly`.
        HTTPError
            If fetching any of the underlying graphs fails.
        URLError
            If connection to KEGG fails.
        """
        descendantEnzymeGraph = self.childClade.coreMetabolismEnzymes(majorityPercentageCoreMetabolism)
        geneDuplicationModel = SimpleGeneDuplication
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        newECs = GeneFunctionAddition.getECs(parentCoreMetabolism, childCoreMetabolism)
        neofunctionalisedMetabolismEnzymes = MajorityNeofunctionalisation.filterEnzymes(descendantEnzymeGraph, geneDuplicationModel, newECs, self.childClade.organismsCount,  majorityPercentage = majorityPercentageGeneDuplication, eValue = defaultEValue)
        
        if colour is True:
            neofunctionalisedMetabolismEnzymesOnly = neofunctionalisedMetabolismEnzymes
            neofunctionalisedMetabolismEnzymes = self.unifiedMetabolismEnzymes(majorityPercentageCoreMetabolism = majorityPercentageCoreMetabolism, colour = True)
            Export.addColourAttribute(neofunctionalisedMetabolismEnzymes, Export.Colour.GREEN, nodes = False, edges = neofunctionalisedMetabolismEnzymesOnly.getEdges())
            
        neofunctionalisedMetabolismEnzymes.name = 'Neofunctionalised metabolism enzymes ' + ' '.join(self.parentNCBInames) + ' -> ' + ' '.join(self.childNCBInames)
        return neofunctionalisedMetabolismEnzymes
    
    def neofunctionalisedMetabolismEnzymesSet(self, majorityPercentageCoreMetabolism = defaultMajorityPercentageCoreMetabolism, majorityPercentageGeneDuplication = defaultMajorityPercentageGeneDuplication) -> Set[Enzyme]:
        """
        Same as :func:`neofunctionalisedMetabolismEnzymes` . :func:`getECs`, but faster.
        """
        descendantEnzymeGraph = self.childClade.coreMetabolismEnzymes(majorityPercentageCoreMetabolism)
        geneDuplicationModel = SimpleGeneDuplication
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        newECs = GeneFunctionAddition.getECs(parentCoreMetabolism, childCoreMetabolism)
        neofunctionalisedEnzymes = MajorityNeofunctionalisation.getEnzymes(descendantEnzymeGraph, geneDuplicationModel, newECs, self.childClade.organismsCount,  majorityPercentage = majorityPercentageGeneDuplication, eValue = defaultEValue)
        return neofunctionalisedEnzymes

    
    


class NestedCladePair(CladePair):
    
    def __init__(self, parent, child, excludeUnclassified = defaultExcludeUnclassified):
        """
        Two clades in NCBI taxonomy, 'child' is assumed younger and must be nested somewhere inside 'parent'.
        
        This only checks nestedness for the first node found in taxonomy, by the first parent's/child's NCBI name, respectively. The latter being relevant if you pass a :class:`Clade`, which has a list of NCBI names, or a list of NCBI names itself.
        
        Parameters
        ----------
        parent : str or List[str] or Clade
            Path(s) of the parent clade's taxon, as defined by NCBI taxonomy, e.g. 'Proteobacteria/Gammaproteobacteria'. Or a ready :class:`Clade` object.
        child : str or List[str] or Clade
            Path(s) of the child clade's taxon, as defined by NCBI taxonomy, e.g. 'Enterobacter'. Or a ready :class:`Clade` object.
        excludeUnclassified : bool, optional
            If *True*, ignore taxons with a path containing the string 'unclassified'.
        
        Attributes
        ----------
        self.childClade : :class:`Clade`
        self.parentClade : :class:`Clade`
        
        Raises
        ------
        ValueError
            If parent or child are unknown taxons. Or if the child taxon is not actually a child of the parent taxon.
        """
        # read first NCBI name from Clade object, if necessary
        if isinstance(parent, Clade):
            parentNCBIname = parent.ncbiNames[0]
        elif not isinstance(parent, str):
            # must be iterable, else fail
            parentNCBIname = parent[0]
        
        if isinstance(child, Clade):
            childNCBIname = child.ncbiNames[0]
        elif not isinstance(child, str):
            # must be iterable, else fail
            childNCBIname = child[0]
            
        # check if child is really a child of parent
        taxonomy = NCBI.getTaxonomy()
        parentNode = taxonomy.searchNodesByPath(parentNCBIname, exceptPaths=('unclassified' if excludeUnclassified else None))
        if parentNode is None or len(parentNode) == 0:
            raise ValueError("No clade of this path found: " + parentNCBIname)
        else: # only consider first element
            parentNode = parentNode[0]
        
        childNode = taxonomy.searchNodesByPath(childNCBIname, exceptPaths=('unclassified' if excludeUnclassified else None))
        if childNode is None or len(childNode) == 0:
            raise ValueError("No clade of this path found: " + childNCBIname)
        else: # only consider first element
            childNode = childNode[0]
        
        foundParent = False
        for ancestor in childNode.ancestors:
            if Taxonomy.nodePath2String(ancestor) == Taxonomy.nodePath2String(parentNode):
                foundParent = True
                break
        
        if foundParent == False:
            raise ValueError("Child is not a descendant of parent.")
        
        super().__init__(parent, child, excludeUnclassified)
