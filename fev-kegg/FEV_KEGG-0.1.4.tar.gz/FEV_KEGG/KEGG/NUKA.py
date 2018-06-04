from FEV_KEGG.Graph import SubstrateGraphs
from FEV_KEGG.Graph.Elements import Reaction, EcNumber
from FEV_KEGG.Graph.SubstrateGraphs import SubstrateEcGraph, SubstrateReactionGraph
from FEV_KEGG.KEGG.File import cache
from FEV_KEGG.KEGG.Organism import Organism
from FEV_KEGG.settings import verbosity as init_verbosity


class NUKA(object):
    
    def __init__(self):
        """
        This is a hypothetical 'complete' organism - NUKA - which possesses all EC numbers known to all metabolic KEGG pathways.
        
        Conversions to other graph types are not possible, because as a hypothetical organism, NUKA has no genes.
        
        Attributes
        ----------
        self.nameAbbreviation : str
        """
        self.nameAbbreviation = 'NUKA'
        
    
    @property
    @cache(folder_path = 'NUKA/graph', file_name = 'SubstrateReactionGraph')
    def substrateReactionGraph(self) -> SubstrateReactionGraph:
        """
        NUKA's substrate-reaction graph.
        
        Returns
        -------
        SubstrateReactionGraph
            Contains all substrates/products and all reactions known to KEGG's metabolic pathways.
        
        Raises
        ------
        HTTPError
            If any underlying organism, pathway, or gene does not exist.
        URLError
            If connection to KEGG fails.
        
        Note
        ----
        This SubstrateReactionGraph can **NOT** be converted into a SubstrateGeneGraph, as the pathways do not contain gene information!
        """
        mockOrganism = Organism('ec') # 'ec' is not an organism abbreviation, but merely desribes that pathways shall contain EC numbers as edges. This returns the full pathways not specific to any species.
        pathwaysSet = mockOrganism.getMetabolicPathways(includeOverviewMaps = False)
        substrateReactionGraph = SubstrateGraphs.Conversion.KeggPathwaySet2SubstrateReactionGraph(pathwaysSet, localVerbosity = 0)
        substrateReactionGraph.name = 'Substrate-Reaction NUKA'
        
        if init_verbosity > 0:
            print('calculated ' + substrateReactionGraph.name)
        
        return substrateReactionGraph
    
    
    @property
    @cache(folder_path = 'NUKA/graph', file_name = 'SubstrateEcGraph')
    def substrateEcGraph(self) -> SubstrateEcGraph:
        """
        NUKA's substrate-EC graph.
        
        Returns
        -------
        SubstrateEcGraph
            Contains all substrates/products and all EC numbers known to KEGG's metabolic pathways.
            
        Raises
        ------
        HTTPError
            If any underlying organism, pathway, or gene does not exist.
        URLError
            If connection to KEGG fails.
        """
        return self._SubstrateReactionGraph2SubstrateEcGraph(self.substrateReactionGraph)
        
        
    def _SubstrateReactionGraph2SubstrateEcGraph(self, speciesSubstrateReactionGraph: SubstrateReactionGraph) -> SubstrateEcGraph:
        """
        Converts NUKA's substrate-reaction graph into a substrate-EC graph. Uses pathway information embedded into the graph object.
        
        Parameters
        ----------
        speciesSubstrateReactionGraph : SubstrateReactionGraph
            NUKA's substrate-reaction graph.
        
        Returns
        -------
        SubstrateEcGraph
            NUKA's substrate-EC graph.
        
        Warnings
        --------
        This function is special to NUKA and **MUST NOT** be used anywhere else!
        """
        # shallow-copy old graph to new graph
        graph = SubstrateEcGraph(speciesSubstrateReactionGraph.underlyingRawGraph)
        graph.name = 'Substrate-EC NUKA'
        
        # create dict of replacements: reaction -> {EC numbers}
        replacementDict = dict()
        
        # for each embedded pathway, get list of 'enzyme' entries
        for pathway in speciesSubstrateReactionGraph.pathwaySet:
            ecEntryList = [e for e in pathway.entries.values() if e.type == 'enzyme']
            
            # for each EC number, get reactions in which it is involved
            for ecEntry in ecEntryList:
                reactionIDList = ecEntry.reaction.split()
                if len(reactionIDList) > 0: # filter EC numbers not associated with any reaction
                    ecNumberList = ecEntry.name.split()
                    
                    # replace each reaction with its associated EC number
                    for reactionID in reactionIDList:
                        reactionName = reactionID.split(':', 1)[1]
                        reaction = Reaction(reactionName)
                        
                        # save associated EC numbers in a set
                        ecNumberSet = set()
                        for ecNumberString in ecNumberList:
                            ecNumber = EcNumber(ecNumberString.replace('ec:', ''))
                            ecNumberSet.add(ecNumber)
                        
                        # update the replacement dict for the current reaction, adding the newly created EC number set
                        replacementSet = replacementDict.get(reaction, None)
                        if replacementSet == None or replacementSet.__class__ != set:
                            replacementSet = set()
                        replacementSet.update(ecNumberSet)
                        replacementDict[reaction] = replacementSet
        
        # get list of all reaction edges. Copy edge list to prevent changes in-place, which would NOT work
        edgeList = list(graph.getEdges())
            
        # replace reaction edges with EC number edges, using replacement dict
        for edge in edgeList:
            substrate, product, reaction = edge
            
            # delete old edge
            graph.removeEdge(substrate, product, reaction, False)
            
            # add new edges, according to replacement dict
            replacementSet = replacementDict[reaction]
            for ecNumber in replacementSet:
                graph.addEC(substrate, product, ecNumber, False)
        
        if init_verbosity > 0:
            print('calculated ' + graph.name)
        
        return graph
    