import math

from typing import Set, Dict

from FEV_KEGG.Graph.Elements import Enzyme, EcNumber
from FEV_KEGG.Graph.SubstrateGraphs import SubstrateEnzymeGraph, SubstrateEcGraph
from FEV_KEGG.KEGG import Database
from builtins import set
from FEV_KEGG.KEGG.Organism import Group
from _collections_abc import Iterable
from FEV_KEGG import settings

defaultEValue = settings.defaultEvalue
"""
Default threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
This can be overridden in each relevant method's `eValue` parameter in this module.
"""
defaultMajorityPercentageGeneDuplication = 70
"""
Default percentage of organisms in the descendant group, which have to possess a neofunctionalised enzyme associated with the same EC number, for it to be included in the set of neofunctionalised enzymes / EC numbers.
Only necessary for :class:`MajorityNeofunctionalisation`, see :func:`MajorityNeofunctionalisation.getEnzymesForEC`.
This can be overridden in each relevant method's `majorityPercentage` parameter, or by using the `majorityTotal` parameter.
"""

class GeneFunctionConservation(object):
    """
    Evolutionary event of conserving a gene function (EC number) between a pair of arbitrary ancestor and descendant.
    
    The conditions for a gene function conservation are:
        - The EC number has been conserved, along the way from an older group of organisms to a newer one.
    """
    @staticmethod
    def getECs(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> Set[EcNumber]:
        """
        Get EC numbers which have been conserved between ancestor and descendant, existing in both.
        
        Parameters
        ----------
        ancestorEcGraph : SubstrateEcGraph
        descendantEcGraph : SubstrateEcGraph
        
        Returns
        -------
        Set[EcNumber]
            Set of EC numbers which occur in the ancestor's EC graph and in the decendants's, i.e. EC numbers which are conserved in the descendant.
        """
        conservedECs = ancestorEcGraph.getECs()
        conservedECs.intersection_update(descendantEcGraph.getECs())
        return conservedECs
    
    @staticmethod
    def getGraph(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> SubstrateEcGraph:
        """
        Get graph containing EC numbers which have been conserved between ancestor and descendant, existing in both.
        
        Parameters
        ----------
        ancestorEcGraph : SubstrateEcGraph
        descendantEcGraph : SubstrateEcGraph
        
        Returns
        -------
        SubstrateEcGraph
            Graph of EC numbers which occur in the ancestor's EC graph, and in the decendants's, i.e. EC numbers which are conserved in the descendant.
            Substrate-EC-product edges are only included if both graphs, ancestor and descendant, have both nodes, substrate and product.
        """
        conservedGraph = ancestorEcGraph.intersection(descendantEcGraph, addCount=False)
        conservedGraph.removeIsolatedNodes()
        return conservedGraph
    
    
class GeneFunctionAddition(object):
    """
    Evolutionary event of adding a gene function (EC number) between a pair of arbitrary ancestor and descendant.
    
    The conditions for a gene function addition are:
        - The EC number has been added, from an unknown origin, along the way from an older group of organisms to a newer one.
    """
    @staticmethod
    def getECs(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> Set[EcNumber]:
        """
        Get EC numbers which have been added between ancestor and descendant, existing only in the descendant.
        
        Parameters
        ----------
        ancestorEcGraph : SubstrateEcGraph
        descendantEcGraph : SubstrateEcGraph
        
        Returns
        -------
        Set[EcNumber]
            Set of EC numbers which occur in the descendant's EC graph, but not in the ancestor's, i.e. EC numbers which are new to the descendant.
        """
        addedECs = descendantEcGraph.getECs()
        addedECs.difference_update(ancestorEcGraph.getECs())
        return addedECs
    
    @staticmethod
    def getGraph(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> SubstrateEcGraph:
        """
        Get graph containing EC numbers which have been added between ancestor and descendant, existing only in the descendant.
        
        Parameters
        ----------
        ancestorEcGraph : SubstrateEcGraph
        descendantEcGraph : SubstrateEcGraph
        
        Returns
        -------
        SubstrateEcGraph
            Graph of EC numbers which occur in the descendant's EC graph, but not in the ancestor's, i.e. EC numbers which are new in the descendant.
            Substrate-EC-product edges are only included if both graphs, ancestor and descendant, have both nodes, substrate and product.
        """
        addedGraph = descendantEcGraph.difference(ancestorEcGraph, subtractNodes=False)
        addedGraph.removeIsolatedNodes()
        return addedGraph


class GeneFunctionLoss(object):
    """
    Evolutionary event of losing a gene function (EC number) between a pair of arbitrary ancestor and descendant.
    
    The conditions for a gene function loss are:
        - The EC number has been lost, along the way from an older group of organisms to a newer one.
    """
    @staticmethod
    def getECs(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> Set[EcNumber]:
        """
        Get EC numbers which have been lost between ancestor and descendant, existing only in the ancestor.
        
        Parameters
        ----------
        ancestorEcGraph : SubstrateEcGraph
        descendantEcGraph : SubstrateEcGraph
        
        Returns
        -------
        Set[EcNumber]
            Set of EC numbers which occur in the ancestor's EC graph, but not in the decendants's, i.e. EC numbers which are lost to the descendant.
        """
        lostECs = ancestorEcGraph.getECs()
        lostECs.difference_update(descendantEcGraph.getECs())
        return lostECs
    
    @staticmethod
    def getGraph(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> SubstrateEcGraph:
        """
        Get graph containing EC numbers which have been lost between ancestor and descendant, existing only in the ancestor.
        
        Parameters
        ----------
        ancestorEcGraph : SubstrateEcGraph
        descendantEcGraph : SubstrateEcGraph
        
        Returns
        -------
        SubstrateEcGraph
            Graph of EC numbers which occur in the ancestor's EC graph, but not in the decendants's, i.e. EC numbers which are lost in the descendant.
            Substrate-EC-product edges are only included if both graphs, ancestor and descendant, have both nodes, substrate and product.
        """
        lostGraph = ancestorEcGraph.difference(descendantEcGraph, subtractNodes=False)
        lostGraph.removeIsolatedNodes()
        return lostGraph


class GeneFunctionDivergence(object):
    """
    Evolutionary event of diverging (adding or losing) a gene function (EC number) between a pair of arbitrary ancestor and descendant.
    
    The conditions for a gene function divergence are:
        - The EC number exists in an older group of organisms, but not in a newer one, or the other way around.
    """
    @staticmethod
    def getECs(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> Set[EcNumber]:
        """
        Get EC numbers which have diverged between ancestor and descendant, existing only in either one of them.
        
        Obviously, `ancestorEcGraph` and `descendantEcGraph` can be swapped here without changing the result.
        
        Parameters
        ----------
        ancestorEcGraph : SubstrateEcGraph
        descendantEcGraph : SubstrateEcGraph
        
        Returns
        -------
        Set[EcNumber]
            Set of EC numbers which occur in the ancestor's EC graph, but not in the decendants's and vice versa, i.e. EC numbers which only exist in either one of the organism groups.
        """
        divergedECs = ancestorEcGraph.getECs()
        divergedECs.symmetric_difference(descendantEcGraph.getECs())
        return divergedECs
    
    @staticmethod
    def getGraph(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> SubstrateEcGraph:
        """
        Get graph containing EC numbers which have diverged between ancestor and descendant, existing only in either one of them.
        
        Parameters
        ----------
        ancestorEcGraph : SubstrateEcGraph
        descendantEcGraph : SubstrateEcGraph
        
        Returns
        -------
        SubstrateEcGraph
            Graph of EC numbers which occur in the ancestor's EC graph, but not in the decendants's and vice versa, i.e. EC numbers which only exist in either one of the organism groups.
            Substrate-EC-product edges are only included if both graphs, ancestor and descendant, have both nodes, substrate and product.
        """
        addedGraph = GeneFunctionAddition.getGraph(ancestorEcGraph, descendantEcGraph)
        lostGraph = GeneFunctionLoss.getGraph(ancestorEcGraph, descendantEcGraph)
        divergedGraph = addedGraph.union(lostGraph, addCount=False)
        return divergedGraph






class GeneDuplication(object): 
    """
    Abstract class for any type of gene duplication.
    """

class SimpleGeneDuplication(GeneDuplication):
    """
    Evolutionary event of duplicating a gene, regardless of ancestoral bonds.
    
    The conditions for a 'simple' gene duplication are:
        - The gene has at least one paralog.
    """    
    @staticmethod
    def getEnzymesFromSet(enzymes: Set[Enzyme], eValue = defaultEValue) -> Set[Enzyme]:
        """
        Get gene-duplicated enzymes.
        
        Parameters
        ----------
        enzymes : Set[Enzyme]
            Set of enzymes to be checked for gene duplication.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        Set[Enzyme]
            All enzymes in `enzymes` which fulfil the conditions of this gene duplication definition.
        
        Raises
        ------
        ValueError
            If any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        possibleGeneDuplicates = set()
        
        geneIDs = [enzyme.geneID for enzyme in enzymes]
        
        matchingsDict = Database.getParalogsBulk(geneIDs, eValue)
        
        for enzyme in enzymes:
            matching = matchingsDict[enzyme.geneID]
            paralogs = matching.matches
            if len(paralogs) > 0:
                possibleGeneDuplicates.add(enzyme)
        
        return possibleGeneDuplicates
    
    @classmethod
    def getEnzymesFromGraph(cls, substrateEnzymeGraph: SubstrateEnzymeGraph, eValue = defaultEValue) -> Set[Enzyme]:
        """
        Get gene-duplicated enzymes.
        
        Parameters
        ----------
        substrateEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes to be checked for gene duplication.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        Set[Enzyme]
            All enzymes in `substrateEnzymeGraph` which fulfil the conditions of this gene duplication definition.
        
        Raises
        ------
        ValueError
            If any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        return cls.getEnzymesFromSet(substrateEnzymeGraph.getEnzymes(), eValue)
    
    @classmethod
    def filterEnzymes(cls, substrateEnzymeGraph: SubstrateEnzymeGraph, eValue = defaultEValue) -> SubstrateEnzymeGraph:
        """
        Remove all enzymes from a graph which have not been gene-duplicated.
        
        Parameters
        ----------
        substrateEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes to be checked for gene duplication.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        SubstrateEnzymeGraph
            A copy of the `substrateEnzymeGraph` containing only enzymes which fulfil the conditions of this gene duplication definition.
        
        Raises
        ------
        ValueError
            If any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        graph = substrateEnzymeGraph.copy()
        possibleGeneDuplicates = cls.getEnzymesFromGraph(substrateEnzymeGraph, eValue)
        graph.removeAllEnzymesExcept( possibleGeneDuplicates )
        return graph
        
    

class ChevronGeneDuplication(GeneDuplication):
    """
    Evolutionary event of duplicating a gene, in dependence of a certain ancestoral bond.
    
    The conditions for a 'chevron' gene duplication are:
        - The gene has at least one paralog.
        - The gene has at least one ortholog in a pre-defined set of organisms.
    """
    def __init__(self, possiblyOrthologousOrganisms: 'Iterable[Organism] or KEGG.Organism.Group'):
        """
        Chevron gene duplication extends simple gene duplication by limiting the possibly duplicated genes via a set of possibly orthologous organisms.
        In contrast to :class:`SimpleGeneDuplication`, this class has to be instantiated, using the aforementioned set of possibly orthologous organisms. 
        
        Parameters
        ----------
        possiblyOrthologousOrganisms : Iterable[Organism] or Organism.Group
            Organisms which will be searched for the occurence of orthologs, i.e. are considered ancestoral.
        
        Attributes
        ----------
        self.possiblyOrthologousOrganisms : Iterable[Organism]
        
        Raises
        ------
        ValueError
            If `possiblyOrthologousOrganisms` is of wrong type.
        """
        if isinstance(possiblyOrthologousOrganisms, Group):
            self.possiblyOrthologousOrganisms = possiblyOrthologousOrganisms.organisms
        elif isinstance(possiblyOrthologousOrganisms, Iterable):
            self.possiblyOrthologousOrganisms = possiblyOrthologousOrganisms
        else:
            raise ValueError("'possiblyOrthologusOrganisms' must be of type Iterable or KEGG.Organism.Group")
    
    def getAllOrthologsForEnzymesFromSet(self, enzymes: Set[Enzyme], eValue = defaultEValue) -> Dict[Enzyme, Set[Enzyme]]:
        """
        For each gene-duplicated enzyme in `enzymes`, get **all** orthologs they might stem from.
        
        Only enzymes with at least one paralog are considered for searching orthologs, because this is a very expensive operation, and this is the first condition for this type of gene duplication.
        Orthologs are searched using the `self.possiblyOrthologousOrganisms` attribute of this instance.
        
        Returns
        -------
        Dict[Enzyme, Set[Enzyme]]
            All Enzymes in `enzymes` which fulfil the conditions of this gene duplication definition, each pointing to a set of **all** their possible orthologs.
        
        Raises
        ------
        :class:`FEV_KEGG.KEGG.Database.ImpossiblyOrthologousError`
            If any enzyme from `enzymes` is from an organism which is also in `self.possiblyOrthologousOrganisms`. 
        ValueError
            If any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        
        Warnings
        --------
        This is a very slow and expensive operation, because all orthologs in all `self.possiblyOrthologousOrganisms` for all `enzymes` are retrieved from KEGG.
        While the enzymes used for retrieving are first filtered to the ones with at least one paralog (which is in itself an expensive operation), this usually leaves many enzymes to be used in searching for orthologs.
        You most likely only want to know which `enzymes` have been gene-duplicated, without knowing from which orthologs they might stem. If this is the case, please use :func:`getEnzymesFromSet` instead, which is much faster.
        """
        possibleGeneDuplicates = SimpleGeneDuplication.getEnzymesFromSet(enzymes, eValue)
        
        orthologsDict = dict()
        
        if len( possibleGeneDuplicates ) == 0:
            return orthologsDict
        
        geneIDs = [enzyme.geneID for enzyme in possibleGeneDuplicates]
        
        # reagarding each possibly orthologous organism
        # get orthologs
        matchingsDict = Database.getOrthologsBulk(geneIDs, self.possiblyOrthologousOrganisms, eValue)
        
        # regarding each paralogous enzyme
        for enzyme in possibleGeneDuplicates:
            # save orthologous GeneIDs for future conversion into Enzymes
            matchings = matchingsDict[enzyme.geneID]
            for matching in matchings:
                orthologsMatches = matching.matches
                if len(orthologsMatches) > 0:
                    orthologsGeneIDs = set([match.foundGeneID for match in orthologsMatches])
                    
                    currentEntry = orthologsDict.get(enzyme, None)
                    if currentEntry is None:
                        orthologsDict[enzyme] = orthologsGeneIDs
                    else:
                        orthologsDict[enzyme] = currentEntry.update( orthologsGeneIDs )
        
        # regarding each paralogous enzyme
        for enzyme in possibleGeneDuplicates:
            # convert GeneIDs into Enzymes
            currentEntry = orthologsDict.get(enzyme, None)
            if currentEntry is not None:
                orthologsDict[enzyme] = set( [Enzyme.fromGene(gene) for gene in Database.getGeneBulk(currentEntry).values() ] )

        else:
            return orthologsDict
    
    def getAllOrthologsForEnzymesFromGraph(self, substrateEnzymeGraph: SubstrateEnzymeGraph, eValue = defaultEValue) -> Dict[Enzyme, Set[Enzyme]]:
        """
        For each gene-duplicated enzyme in `substrateEnzymeGraph`, get **all** orthologs they might stem from.
        
        Only enzymes with at least one paralog are considered for searching orthologs, because this is a very expensive operation, and this is the first condition for this type of gene duplication.
        Orthologs are searched using the `self.possiblyOrthologousOrganisms` attribute of this instance.
        
        Returns
        -------
        Dict[Enzyme, Set[Enzyme]]
            All Enzymes in `substrateEnzymeGraph` which fulfil the conditions of this gene duplication definition, each pointing to a set of **all** their possible orthologs.
        
        Raises
        ------
        :class:`FEV_KEGG.KEGG.Database.ImpossiblyOrthologousError`
            If any enzyme from `enzymes` is from an organism which is also in `self.possiblyOrthologousOrganisms`. 
        ValueError
            If any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        
        Warnings
        --------
        This is a very slow and expensive operation, because all orthologs in all `self.possiblyOrthologousOrganisms` for all enzymes are retrieved from KEGG.
        While the enzymes used for retrieving are first filtered to the ones with at least one paralog (which is in itself an expensive operation), this usually leaves many enzymes to be used in searching for orthologs.
        You most likely only want to know which enzymes have been gene-duplicated, without knowing from which orthologs they might stem. If this is the case, please use :func:`getEnzymesFromGraph` instead, which is much faster.
        """
        return self.getAllOrthologsForEnzymesFromSet(substrateEnzymeGraph.getEnzymes(), eValue)
    
    
    def getEnzymesFromSet(self, enzymes: Set[Enzyme], eValue = defaultEValue) -> Set[Enzyme]:
        """
        Get gene-duplicated enzymes.
        
        Parameters
        ----------
        enzymes : Set[Enzyme]
            Set of enzymes to be checked for gene duplication.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        Set[Enzyme]
            All enzymes in `enzymes` which fulfil the conditions of this gene duplication definition.
        
        Raises
        ------
        ValueError
            If any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        possibleGeneDuplicates = SimpleGeneDuplication.getEnzymesFromSet(enzymes, eValue)
        
        if len( possibleGeneDuplicates ) == 0:
            return possibleGeneDuplicates
        
        soughtEnzymes = possibleGeneDuplicates
        
        # ensure deterministic behaviour. Otherwise, this would null the use of the cache.
        sortedOrganisms = []
        sortedOrganisms.extend( self.possiblyOrthologousOrganisms )
        sortedOrganisms.sort()
        
        duplicatedEnzymes = set()
        
        # reagarding each possibly orthologous organism
        for comparisonOrganism in sortedOrganisms:
            
            # break if nothing left to search for
            if len(soughtEnzymes) == 0:
                break
            
            # get orthologs
            geneIDs = [enzyme.geneID for enzyme in soughtEnzymes]
            matchingsDict = Database.getOrthologsBulk(geneIDs, [comparisonOrganism], eValue)
            
            enzymesToRemove = set()
            
            # regarding each paralogous enzyme still sought
            for enzyme in soughtEnzymes:
                # count orthologous GeneIDs
                matching = matchingsDict[enzyme.geneID]
                orthologsMatches = matching.matches
                if len(orthologsMatches) > 0:
                    duplicatedEnzymes.add(enzyme)
                    enzymesToRemove.add(enzyme)
                    
            # remove found Enzyme from list of sought after Enzymes
            soughtEnzymes.difference_update(enzymesToRemove)
        
        return duplicatedEnzymes
    
    def getEnzymesFromGraph(self, substrateEnzymeGraph: SubstrateEnzymeGraph, eValue = defaultEValue) -> Set[Enzyme]:
        """
        Get gene-duplicated enzymes.
        
        Parameters
        ----------
        substrateEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes to be checked for gene duplication.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        Set[Enzyme]
            All enzymes in `substrateEnzymeGraph` which fulfil the conditions of this gene duplication definition.
        
        Raises
        ------
        ValueError
            If any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        return self.getEnzymesFromSet(substrateEnzymeGraph.getEnzymes(), eValue)
    
    def filterEnzymes(self, substrateEnzymeGraph: SubstrateEnzymeGraph, eValue = defaultEValue) -> SubstrateEnzymeGraph:
        """
        Remove all enzymes from a graph which have not been gene-duplicated.
        
        Parameters
        ----------
        substrateEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes to be checked for gene duplication.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        SubstrateEnzymeGraph
            A copy of the `substrateEnzymeGraph` containing only enzymes which fulfil the conditions of this gene duplication definition.
        
        Raises
        ------
        ValueError
            If any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        graph = substrateEnzymeGraph.copy()
        possibleGeneDuplicates = self.getEnzymesFromGraph(substrateEnzymeGraph, eValue)
        graph.removeAllEnzymesExcept( possibleGeneDuplicates )
        return graph






class Neofunctionalisation(object):
    """
    Abstract class for any type of neofunctionalisation.
    
    The conditions for a neofunctionalisation are:
        - The gene has been duplicated, along the way from an older group of organisms to a newer one, according to a certain class of GeneDuplication.
        - The duplicated gene is associated with an EC number which does not occur in the older group of organisms.
    """
    getNewECs = GeneFunctionAddition.getECs
    


class AnyNeofunctionalisation(Neofunctionalisation):
    """
    Evolutionary event of duplicating a gene, and then changing the function (EC number), within any organism of the group.
    
    Regarding groups of organisms, the conditions of this neofunctionalisation extend by:
        - At least one organism of the descendant group has to contain a gene-duplicated enzyme for it (the enzyme or its EC number) to be reported.
    """
    @staticmethod
    def getEnzymesForEC(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                        newECs: Set[EcNumber], eValue = defaultEValue) -> Dict[EcNumber, Set[Enzyme]]:
        """
        Get EC numbers which have arisen due to neofunctionalisation, in any organism of the descendant group, pointing to their associated neofunctionalised enzymes.
        
        Parameters
        ----------
        descendantEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes occuring in the whole descendant organism group. Also called the collective enzyme graph, see :func:`FEV_KEGG.KEGG.Organism.Group.collectiveEnzymeGraph`.
        geneDuplicationModel : GeneDuplication
            Model to be used to determine whether a gene duplication event occured. If the model you chose does not require instantiation, you may pass the class name.
        newECs : Set[EcNumber]
            EC numbers which are, in comparison to a certain ancestor organism group, new to the descendant organism group represented by `descendantEnzymeGraph`.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        Dict[EcNumber, Set[Enzyme]]
            Dictionary of Sets of Enzymes which fulfil the conditions of neofunctionalisation, keyed by the new EC numbers they encode.
        
        Raises
        ------
        NotImplementedError
            If the chosen `geneDuplicationModel` is unknown and, therefore, can not be used here.
        ValueError
            If the chosen `geneDuplicationModel` requires instantiation, but only the class was given. Or if any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        result = dict()
        
        # for each new EC number, get enzymes in descendant
        for ecNumber in newECs:
            enzymes = descendantEnzymeGraph.getEnzymesForEcNumber(ecNumber)
            
            # which of these enzymes have been subject to gene duplication? Report them.
            if isinstance(geneDuplicationModel, SimpleGeneDuplication) or geneDuplicationModel == SimpleGeneDuplication:
                duplicatedEnzymes = geneDuplicationModel.getEnzymesFromSet(enzymes, eValue)
            
            elif geneDuplicationModel == ChevronGeneDuplication:
                raise ValueError("Chevron gene duplication model requires you to instantiate an object, parametrised with the set of possibly orthologous organisms.")
                
            elif isinstance(geneDuplicationModel, ChevronGeneDuplication):
                duplicatedEnzymes = geneDuplicationModel.getEnzymesFromSet(enzymes, eValue)
                
            else:
                raise NotImplementedError('gene duplication model not yet known: ' + str(geneDuplicationModel))
            
            if len(duplicatedEnzymes) != 0:
                result[ecNumber] = duplicatedEnzymes 
        
        return result
    
    @staticmethod
    def getEnzymes(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                   newECs: Set[EcNumber], eValue = defaultEValue) -> Set[Enzyme]:
        """
        Get enzymes which have been neofunctionalised, in any organism of the descendant group.
        
        Parameters
        ----------
        descendantEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes occuring in the whole descendant organism group. Also called the collective enzyme graph, see :func:`FEV_KEGG.KEGG.Organism.Group.collectiveEnzymeGraph`.
        geneDuplicationModel : GeneDuplication
            Model to be used to determine whether a gene duplication event occured. If the model you chose does not require instantiation, you may pass the class name.
        newECs : Set[EcNumber]
            EC numbers which are, in comparison to a certain ancestor organism group, new to the descendant organism group represented by `descendantEnzymeGraph`.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        Set[Enzyme]
            Set of Enzymes which fulfil the conditions of this neofunctionalisation.
        
        Raises
        ------
        NotImplementedError
            If the chosen `geneDuplicationModel` is unknown and, therefore, can not be used here.
        ValueError
            If the chosen `geneDuplicationModel` requires instantiation, but only the class was given. Or if any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        resultDict = AnyNeofunctionalisation.getEnzymesForEC(descendantEnzymeGraph, geneDuplicationModel, newECs, eValue)
        resultSets = resultDict.values()
        result = set()
        for resultSet in resultSets:
            result.update( resultSet )
        return result
    
    @staticmethod
    def filterEnzymes(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                      newECs: Set[EcNumber], eValue = defaultEValue) -> SubstrateEnzymeGraph:
        """
        Remove all enzymes from a graph which have not been neofunctionalised, in any organism of the descendant group.
        
        Parameters
        ----------
        descendantEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes occuring in the whole descendant organism group. Also called the collective enzyme graph, see :func:`FEV_KEGG.KEGG.Organism.Group.collectiveEnzymeGraph`.
        geneDuplicationModel : GeneDuplication
            Model to be used to determine whether a gene duplication event occured. If the model you chose does not require instantiation, you may pass the class name.
        newECs : Set[EcNumber]
            EC numbers which are, in comparison to a certain ancestor organism group, new to the descendant organism group represented by `descendantEnzymeGraph`.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        SubstrateEnzymeGraph
            Copy of the descendant's SubstrateEnzymeGraph containing only Enzymes which fulfil the conditions of this neofunctionalisation.
        
        Raises
        ------
        NotImplementedError
            If the chosen `geneDuplicationModel` is unknown and, therefore, can not be used here.
        ValueError
            If the chosen `geneDuplicationModel` requires instantiation, but only the class was given. Or if any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        graph = descendantEnzymeGraph.copy()
        possibleNeofunctionalisations = AnyNeofunctionalisation.getEnzymes(descendantEnzymeGraph, geneDuplicationModel, newECs, eValue)
        graph.removeAllEnzymesExcept( possibleNeofunctionalisations )
        return graph
    
    @staticmethod
    def getECs(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
               newECs: Set[EcNumber], eValue = defaultEValue) -> Set[EcNumber]:
        """
        Get EC numbers which have arisen due to neofunctionalisation, in any organism of the descendant group.
        
        Parameters
        ----------
        descendantEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes occuring in the whole descendant organism group. Also called the collective enzyme graph, see :func:`FEV_KEGG.KEGG.Organism.Group.collectiveEnzymeGraph`.
        geneDuplicationModel : GeneDuplication
            Model to be used to determine whether a gene duplication event occured. If the model you chose does not require instantiation, you may pass the class name.
        newECs : Set[EcNumber]
            EC numbers which are, in comparison to a certain ancestor organism group, new to the descendant organism group represented by `descendantEnzymeGraph`.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        Set[EcNumber]
            Set of EC numbers associated with genes which fulfil the conditions of this neofunctionalisation
        
        Raises
        ------
        NotImplementedError
            If the chosen `geneDuplicationModel` is unknown and, therefore, can not be used here.
        ValueError
            If the chosen `geneDuplicationModel` requires instantiation, but only the class was given. Or if any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        return set( AnyNeofunctionalisation.getEnzymesForEC(descendantEnzymeGraph, geneDuplicationModel, newECs, eValue).keys() )
    
    @staticmethod
    def filterECs(descendantEcGraph: SubstrateEcGraph,
                  descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                  newECs: Set[EcNumber], eValue = defaultEValue) -> SubstrateEcGraph:
        """
        Remove all EC numbers from a graph which have not arisen from neofunctionalisation, in any organism of the descendant group.
        
        Parameters
        ----------
        descendantEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes occuring in the whole descendant organism group. Also called the collective enzyme graph, see :func:`FEV_KEGG.KEGG.Organism.Group.collectiveEnzymeGraph`.
        geneDuplicationModel : GeneDuplication
            Model to be used to determine whether a gene duplication event occured. If the model you chose does not require instantiation, you may pass the class name.
        newECs : Set[EcNumber]
            EC numbers which are, in comparison to a certain ancestor organism group, new to the descendant organism group represented by `descendantEnzymeGraph`.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        SubstrateEcGraph
            Copy of the descendant's SubstrateEcGraph containing only EC numbers associated with genes which fulfil the condition of this neofunctionalisation.
        
        Raises
        ------
        NotImplementedError
            If the chosen `geneDuplicationModel` is unknown and, therefore, can not be used here.
        ValueError
            If the chosen `geneDuplicationModel` requires instantiation, but only the class was given. Or if any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        graph = descendantEcGraph.copy()
        possibleNeofunctionalisations = AnyNeofunctionalisation.getECs(descendantEnzymeGraph, geneDuplicationModel, newECs, eValue)
        graph.removeAllECsExcept( possibleNeofunctionalisations )
        return graph
    
        

class MajorityNeofunctionalisation(Neofunctionalisation):
    """
    Evolutionary event of duplicating a gene, and then changing the function (EC number), within the majority of organisms of the group.
    
    Regarding groups of organisms, the conditions of this neofunctionalisation extend by:
        - The majority of organisms of the descendant group has to contain a gene-duplicated enzyme for it (the enzyme or its EC number) to be reported.
    """
    @staticmethod
    def getEnzymesForEC(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                        newECs: Set[EcNumber], descendantOrganismsCount, majorityPercentage = defaultMajorityPercentageGeneDuplication, majorityTotal = None, eValue = defaultEValue) -> Dict[EcNumber, Set[Enzyme]]:
        """
        Get EC numbers which have arisen due to neofunctionalisation, in the majority of organisms of the descendant group, pointing to their associated neofunctionalised enzymes.
        
        Parameters
        ----------
        descendantEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes occuring in the whole descendant organism group. Also called the collective enzyme graph, see :func:`FEV_KEGG.KEGG.Organism.Group.collectiveEnzymeGraph`.
        geneDuplicationModel : GeneDuplication
            Model to be used to determine whether a gene duplication event occured. If the model you chose does not require instantiation, you may pass the class name.
        newECs : Set[EcNumber]
            EC numbers which are, in comparison to a certain ancestor organism group, new to the descendant organism group represented by `descendantEnzymeGraph`.
        descendantOrganismsCount : int
            Number of organisms in the descendant organism group.
        majorityPercentage : float, optional
            Because the enzymes are usually from different organisms, `majorityPercentage` % percent of all organisms in the descendant organism group have to possess a neofunctionalised enzyme associated with the same EC number, for this enzyme to be returned.
        majorityTotal : int, optional
            If given (not *None*), `majorityPercentage` is ignored and the percentage of organisms for a majority is calculated from `majorityTotal`.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        Dict[EcNumber, Set[Enzyme]]
            Dictionary of Sets of Enzymes which fulfil the conditions of neofunctionalisation, keyed by the new EC numbers they encode.
        
        Raises
        ------
        NotImplementedError
            If the chosen `geneDuplicationModel` is unknown and, therefore, can not be used here.
        ValueError
            If the chosen `geneDuplicationModel` requires instantiation, but only the class was given. Or if any organism does not exist. Or if `majorityPercentage` is not a valid percentage.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        # check if majority is sane
        if majorityTotal is not None:
            percentage = majorityTotal / descendantOrganismsCount * 100
        else:
            percentage = majorityPercentage
            
        if percentage <= 0 or percentage > 100:
            raise ValueError('Majority percentage is not a sane value (0 < percentage <= 100): ' + str(percentage))
        
        majority = math.ceil((percentage/100) * int( descendantOrganismsCount ) )
        
        # get neofunctionalised enzymes dict
        neofunctionalisedEnzymes = AnyNeofunctionalisation.getEnzymesForEC(descendantEnzymeGraph, geneDuplicationModel, newECs, eValue)
        
        # for each new EC number, check if enough organisms have at least one neofunctionalised enzyme associated with this new EC number
        result = dict()
        for ecNumber, enzymesSet in neofunctionalisedEnzymes.items():
            
            organismsCount = dict()
            for enzyme in enzymesSet:
                organismsCount[ enzyme.organismAbbreviation ] = True
            
            # if so, report the EC number.
            if len( organismsCount.keys() ) >= majority:
                result[ ecNumber ] = enzymesSet
        
        return result
    
    @staticmethod
    def getEnzymes(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                   newECs: Set[EcNumber], descendantOrganismsCount, majorityPercentage = defaultMajorityPercentageGeneDuplication, majorityTotal = None, eValue = defaultEValue) -> Set[Enzyme]:
        """
        Get enzymes which have been neofunctionalised, in the majority of organisms of the descendant group.
        
        Parameters
        ----------
        descendantEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes occuring in the whole descendant organism group. Also called the collective enzyme graph, see :func:`FEV_KEGG.KEGG.Organism.Group.collectiveEnzymeGraph`.
        geneDuplicationModel : GeneDuplication
            Model to be used to determine whether a gene duplication event occured. If the model you chose does not require instantiation, you may pass the class name.
        newECs : Set[EcNumber]
            EC numbers which are, in comparison to a certain ancestor organism group, new to the descendant organism group represented by `descendantEnzymeGraph`.
        descendantOrganismsCount : int
            Number of organisms in the descendant organism group.
        majorityPercentage : float, optional
            Because the enzymes are usually from different organisms, `majorityPercentage` % percent of all organisms in the descendant organism group have to possess a neofunctionalised enzyme associated with the same EC number, for this enzyme to be returned.
        majorityTotal : int, optional
            If given (not *None*), `majorityPercentage` is ignored and the percentage of organisms for a majority is calculated from `majorityTotal`.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        Set[Enzyme]
            Set of Enzymes which fulfil the conditions of this neofunctionalisation.
        
        Raises
        ------
        NotImplementedError
            If the chosen `geneDuplicationModel` is unknown and, therefore, can not be used here.
        ValueError
            If the chosen `geneDuplicationModel` requires instantiation, but only the class was given. Or if any organism does not exist. Or if `majorityPercentage` is not a valid percentage.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        resultDict = MajorityNeofunctionalisation.getEnzymesForEC(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage, majorityTotal, eValue)
        resultSets = resultDict.values()
        result = set()
        for resultSet in resultSets:
            result.update( resultSet )
        return result
    
    @staticmethod
    def filterEnzymes(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                      newECs: Set[EcNumber], descendantOrganismsCount, majorityPercentage = defaultMajorityPercentageGeneDuplication, majorityTotal = None, eValue = defaultEValue) -> SubstrateEnzymeGraph:
        """
        Remove all enzymes from a graph which have not been neofunctionalised, in all organisms of the descendant group.
        
        Parameters
        ----------
        descendantEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes occuring in the whole descendant organism group. Also called the collective enzyme graph, see :func:`FEV_KEGG.KEGG.Organism.Group.collectiveEnzymeGraph`.
        geneDuplicationModel : GeneDuplication
            Model to be used to determine whether a gene duplication event occured. If the model you chose does not require instantiation, you may pass the class name.
        newECs : Set[EcNumber]
            EC numbers which are, in comparison to a certain ancestor organism group, new to the descendant organism group represented by `descendantEnzymeGraph`.
        descendantOrganismsCount : int
            Number of organisms in the descendant organism group.
        majorityPercentage : float, optional
            Because the enzymes are usually from different organisms, `majorityPercentage` % percent of all organisms in the descendant organism group have to possess a neofunctionalised enzyme associated with the same EC number, for this enzyme to be returned.
        majorityTotal : int, optional
            If given (not *None*), `majorityPercentage` is ignored and the percentage of organisms for a majority is calculated from `majorityTotal`.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        SubstrateEnzymeGraph
            Copy of the descendant's SubstrateEnzymeGraph containing only Enzymes which fulfil the conditions of this neofunctionalisation.
        
        Raises
        ------
        NotImplementedError
            If the chosen `geneDuplicationModel` is unknown and, therefore, can not be used here.
        ValueError
            If the chosen `geneDuplicationModel` requires instantiation, but only the class was given. Or if any organism does not exist. Or if `majorityPercentage` is not a valid percentage.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        graph = descendantEnzymeGraph.copy()
        possibleNeofunctionalisations = MajorityNeofunctionalisation.getEnzymes(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage, majorityTotal, eValue)
        graph.removeAllEnzymesExcept( possibleNeofunctionalisations )
        return graph
    
    @staticmethod
    def getECs(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
               newECs: Set[EcNumber], descendantOrganismsCount, majorityPercentage = defaultMajorityPercentageGeneDuplication, majorityTotal = None, eValue = defaultEValue) -> Set[EcNumber]:
        """
        Get EC numbers which have arisen due to neofunctionalisation, in all organisms of the descendant group.
        
        Parameters
        ----------
        descendantEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes occuring in the whole descendant organism group. Also called the collective enzyme graph, see :func:`FEV_KEGG.KEGG.Organism.Group.collectiveEnzymeGraph`.
        geneDuplicationModel : GeneDuplication
            Model to be used to determine whether a gene duplication event occured. If the model you chose does not require instantiation, you may pass the class name.
        newECs : Set[EcNumber]
            EC numbers which are, in comparison to a certain ancestor organism group, new to the descendant organism group represented by `descendantEnzymeGraph`.
        descendantOrganismsCount : int
            Number of organisms in the descendant organism group.
        majorityPercentage : float, optional
            Because the enzymes are usually from different organisms, `majorityPercentage` % percent of all organisms in the descendant organism group have to possess a neofunctionalised enzyme associated with the same EC number, for this enzyme to be returned.
        majorityTotal : int, optional
            If given (not *None*), `majorityPercentage` is ignored and the percentage of organisms for a majority is calculated from `majorityTotal`.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        Set[EcNumber]
            Set of EC numbers associated with genes which fulfil the conditions of this neofunctionalisation
        
        Raises
        ------
        NotImplementedError
            If the chosen `geneDuplicationModel` is unknown and, therefore, can not be used here.
        ValueError
            If the chosen `geneDuplicationModel` requires instantiation, but only the class was given. Or if any organism does not exist. Or if `majorityPercentage` is not a valid percentage.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        resultDict = MajorityNeofunctionalisation.getEnzymesForEC(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage, majorityTotal, eValue)
        return set( resultDict.keys() )
    
    @staticmethod
    def filterECs(descendantEcGraph: SubstrateEcGraph,
                  descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                  newECs: Set[EcNumber], descendantOrganismsCount, majorityPercentage = defaultMajorityPercentageGeneDuplication, majorityTotal = None, eValue = defaultEValue) -> SubstrateEcGraph:
        """
        Remove all EC numbers from a graph which have not arisen from neofunctionalisation, in the majority of organisms of the descendant group.
        
        Parameters
        ----------
        descendantEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes occuring in the whole descendant organism group. Also called the collective enzyme graph, see :func:`FEV_KEGG.KEGG.Organism.Group.collectiveEnzymeGraph`.
        geneDuplicationModel : GeneDuplication
            Model to be used to determine whether a gene duplication event occured. If the model you chose does not require instantiation, you may pass the class name.
        newECs : Set[EcNumber]
            EC numbers which are, in comparison to a certain ancestor organism group, new to the descendant organism group represented by `descendantEnzymeGraph`.
        descendantOrganismsCount : int
            Number of organisms in the descendant organism group.
        majorityPercentage : float, optional
            Because the enzymes are usually from different organisms, `majorityPercentage` % percent of all organisms in the descendant organism group have to possess a neofunctionalised enzyme associated with the same EC number, for this enzyme to be returned.
        majorityTotal : int, optional
            If given (not *None*), `majorityPercentage` is ignored and the percentage of organisms for a majority is calculated from `majorityTotal`.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        SubstrateEcGraph
            Copy of the descendant's SubstrateEcGraph containing only EC numbers associated with genes which fulfil the condition of this neofunctionalisation.
        
        Raises
        ------
        NotImplementedError
            If the chosen `geneDuplicationModel` is unknown and, therefore, can not be used here.
        ValueError
            If the chosen `geneDuplicationModel` requires instantiation, but only the class was given. Or if any organism does not exist. Or if `majorityPercentage` is not a valid percentage.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        graph = descendantEcGraph.copy()
        possibleNeofunctionalisations = MajorityNeofunctionalisation.getECs(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage, majorityTotal, eValue)
        graph.removeAllECsExcept( possibleNeofunctionalisations )
        return graph



class ConsensusNeofunctionalisation(Neofunctionalisation):
    """
    Evolutionary event of duplicating a gene, and then changing the function (EC number), within all organisms of the group.
    
    Regarding groups of organisms, the conditions of this neofunctionalisation extend by:
        - All organisms of the descendant group has to contain a gene-duplicated enzyme for it (the enzyme or its EC number) to be reported.
    """
    @staticmethod
    def getEnzymesForEC(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                        newECs: Set[EcNumber], descendantOrganismsCount, eValue = defaultEValue) -> Dict[EcNumber, Set[Enzyme]]:
        """
        Get EC numbers which have arisen due to neofunctionalisation, in the majority of organisms of the descendant group, pointing to their associated neofunctionalised enzymes.
        
        Parameters
        ----------
        descendantEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes occuring in the whole descendant organism group. Also called the collective enzyme graph, see :func:`FEV_KEGG.KEGG.Organism.Group.collectiveEnzymeGraph`.
        geneDuplicationModel : GeneDuplication
            Model to be used to determine whether a gene duplication event occured. If the model you chose does not require instantiation, you may pass the class name.
        newECs : Set[EcNumber]
            EC numbers which are, in comparison to a certain ancestor organism group, new to the descendant organism group represented by `descendantEnzymeGraph`.
        descendantOrganismsCount : int
            Number of organisms in the descendant organism group.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        Dict[EcNumber, Set[Enzyme]]
            Dictionary of Sets of Enzymes which fulfil the conditions of neofunctionalisation, keyed by the new EC numbers they encode.
        
        Raises
        ------
        NotImplementedError
            If the chosen `geneDuplicationModel` is unknown and, therefore, can not be used here.
        ValueError
            If the chosen `geneDuplicationModel` requires instantiation, but only the class was given. Or if any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        return MajorityNeofunctionalisation.getEnzymesForEC(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage = 100, majorityTotal = None, eValue = eValue)
    
    @staticmethod
    def getEnzymes(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                   newECs: Set[EcNumber], descendantOrganismsCount, eValue = defaultEValue) -> Set[Enzyme]:
        """
        Get enzymes which have been neofunctionalised, in all organisms of the descendant group.
        
        Parameters
        ----------
        descendantEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes occuring in the whole descendant organism group. Also called the collective enzyme graph, see :func:`FEV_KEGG.KEGG.Organism.Group.collectiveEnzymeGraph`.
        geneDuplicationModel : GeneDuplication
            Model to be used to determine whether a gene duplication event occured. If the model you chose does not require instantiation, you may pass the class name.
        newECs : Set[EcNumber]
            EC numbers which are, in comparison to a certain ancestor organism group, new to the descendant organism group represented by `descendantEnzymeGraph`.
        descendantOrganismsCount : int
            Number of organisms in the descendant organism group.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        Set[Enzyme]
            Set of Enzymes which fulfil the conditions of this neofunctionalisation.
        
        Raises
        ------
        NotImplementedError
            If the chosen `geneDuplicationModel` is unknown and, therefore, can not be used here.
        ValueError
            If the chosen `geneDuplicationModel` requires instantiation, but only the class was given. Or if any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        return MajorityNeofunctionalisation.getEnzymes(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage = 100, majorityTotal = None, eValue = eValue)
    
    @staticmethod
    def filterEnzymes(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                      newECs: Set[EcNumber], descendantOrganismsCount, eValue = defaultEValue) -> SubstrateEnzymeGraph:
        """
        Remove all enzymes from a graph which have not been neofunctionalised, in all organisms of the descendant group.
        
        Parameters
        ----------
        descendantEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes occuring in the whole descendant organism group. Also called the collective enzyme graph, see :func:`FEV_KEGG.KEGG.Organism.Group.collectiveEnzymeGraph`.
        geneDuplicationModel : GeneDuplication
            Model to be used to determine whether a gene duplication event occured. If the model you chose does not require instantiation, you may pass the class name.
        newECs : Set[EcNumber]
            EC numbers which are, in comparison to a certain ancestor organism group, new to the descendant organism group represented by `descendantEnzymeGraph`.
        descendantOrganismsCount : int
            Number of organisms in the descendant organism group.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        SubstrateEnzymeGraph
            Copy of the descendant's SubstrateEnzymeGraph containing only Enzymes which fulfil the conditions of this neofunctionalisation.
        
        Raises
        ------
        NotImplementedError
            If the chosen `geneDuplicationModel` is unknown and, therefore, can not be used here.
        ValueError
            If the chosen `geneDuplicationModel` requires instantiation, but only the class was given. Or if any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        return MajorityNeofunctionalisation.filterEnzymes(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage = 100, majorityTotal = None, eValue = eValue)
    
    @staticmethod
    def getECs(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
               newECs: Set[EcNumber], descendantOrganismsCount, eValue = defaultEValue) -> Set[EcNumber]:
        """
        Get EC numbers which have arisen due to neofunctionalisation, in all organisms of the descendant group.
        
        Parameters
        ----------
        descendantEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes occuring in the whole descendant organism group. Also called the collective enzyme graph, see :func:`FEV_KEGG.KEGG.Organism.Group.collectiveEnzymeGraph`.
        geneDuplicationModel : GeneDuplication
            Model to be used to determine whether a gene duplication event occured. If the model you chose does not require instantiation, you may pass the class name.
        newECs : Set[EcNumber]
            EC numbers which are, in comparison to a certain ancestor organism group, new to the descendant organism group represented by `descendantEnzymeGraph`.
        descendantOrganismsCount : int
            Number of organisms in the descendant organism group.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        Set[EcNumber]
            Set of EC numbers associated with genes which fulfil the conditions of this neofunctionalisation
        
        Raises
        ------
        NotImplementedError
            If the chosen `geneDuplicationModel` is unknown and, therefore, can not be used here.
        ValueError
            If the chosen `geneDuplicationModel` requires instantiation, but only the class was given. Or if any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        return MajorityNeofunctionalisation.getECs(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage = 100, majorityTotal = None, eValue = eValue)
    
    @staticmethod
    def filterECs(descendantEcGraph: SubstrateEcGraph,
                  descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                  newECs: Set[EcNumber], descendantOrganismsCount, eValue = defaultEValue) -> SubstrateEcGraph:
        """
        Remove all EC numbers from a graph which have not arisen from neofunctionalisation, in all organisms of the descendant group.
        
        Parameters
        ----------
        descendantEnzymeGraph : SubstrateEnzymeGraph
            Graph of enzymes occuring in the whole descendant organism group. Also called the collective enzyme graph, see :func:`FEV_KEGG.KEGG.Organism.Group.collectiveEnzymeGraph`.
        geneDuplicationModel : GeneDuplication
            Model to be used to determine whether a gene duplication event occured. If the model you chose does not require instantiation, you may pass the class name.
        newECs : Set[EcNumber]
            EC numbers which are, in comparison to a certain ancestor organism group, new to the descendant organism group represented by `descendantEnzymeGraph`.
        descendantOrganismsCount : int
            Number of organisms in the descendant organism group.
        eValue : float, optional
            Threshold for the statistical expectation value (E-value), below which a sequence alignment is considered significant.
        
        Returns
        -------
        SubstrateEcGraph
            Copy of the descendant's SubstrateEcGraph containing only EC numbers associated with genes which fulfil the condition of this neofunctionalisation.
        
        Raises
        ------
        NotImplementedError
            If the chosen `geneDuplicationModel` is unknown and, therefore, can not be used here.
        ValueError
            If the chosen `geneDuplicationModel` requires instantiation, but only the class was given. Or if any organism does not exist.
        HTTPError
            If any gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        return MajorityNeofunctionalisation.filterECs(descendantEcGraph, descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage = 100, majorityTotal = 100, eValue = eValue)

    