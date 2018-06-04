from FEV_KEGG.Graph.Elements import EcNumber
from FEV_KEGG.Graph.SubstrateGraphs import SubstrateEcGraph
from FEV_KEGG.KEGG.File import cache
from FEV_KEGG.KEGG.NUKA import NUKA
from FEV_KEGG.settings import verbosity as init_verbosity
from enum import Enum
import FEV_KEGG.Evolution.Clade
from typing import Set


class GoldmanLUCA(object):

    def __init__(self):
        """
        This is the Last Universal Common Ancestor, as described in: The Enzymatic and Metabolic Capabilities of Early Life (2012, Goldman et al.) [https://doi.org/10.1371/journal.pone.0039912]
        
        The original work on LUCA, however, does not specify enzyme function, but merely COGs: 
          Algorithms for computing parsimonious evolutionary scenarios for genome evolution, the last universal common ancestor and dominance of horizontal gene transfer in the evolution of prokaryotes (2003, Mirkin et al.) [https://doi.org/10.1186/1471-2148-3-2]
        
        This class already contains the list of LUCA's enzymes from the above paper, as depicted in the first table [https://doi.org/10.1371/journal.pone.0039912.t001]
        As the most plausible minimal set of enzymatic functions, the authors chose the intersection of EC numbers found in universal sequence + structure, combined with the ones found in universal sequence + structure + function. See the original source for details.
        
        This list is parsed and converted into a SubstrateEcGraph.
        Conversion is done by using the graph of a hypothetical 'complete' organism - NUKA - which possesses all EC numbers known to all metabolic KEGG pathways.
        All EC numbers not present in LUCA are filtered out.
        Keep in mind, though, that LUCA's EC numbers only contain three levels, to more adequately model the likely patchwork evolution in ancient times.
        Therefore, all EC numbers starting with the sub-class remain, regardless of substrate specificity.
        
        Conversion into another type of graph is not supported, because LUCA is a strictly hypothetical organism without any exactly known genes.
        """
        self.nameAbbreviation = 'GoldmanLUCA'        
    
    @property
    def ecNumbers(self) -> Set[EcNumber]:    
        lucaEcNumberStrings = [
            '1.3.1.-',
            '2.4.1.-',
            '2.7.1.-',
            '2.7.7.-',
            '3.1.2.-',
            '3.1.4.-',
            '3.2.1.-',
            '3.5.1.-',
            '4.1.2.-',
            '6.3.2.-'
            ]
        
        lucaEcNumbers = set()
        for string in lucaEcNumberStrings:
            lucaEcNumbers.add(EcNumber(string))
        
        return lucaEcNumbers
    
    @property
    @cache(folder_path = 'GoldmanLUCA/graph', file_name = 'SubstrateEcGraph')
    def substrateEcGraph(self) -> SubstrateEcGraph:
        
        lucaEcNumbers = self.ecNumbers
        
        # copy SubstrateEcGraph from NUKA
        graph = NUKA().substrateEcGraph.copy()
        
        # delete all edges with EC numbers that are not contained in the EC numbers of LUCA
        for edge in list(graph.getEdges()): # use a copy, to avoid modification in-place during iteration
            substrate, product, nukaEC = edge
            
            nukaEcContainedInLuca = False
            
            for lucaEC in lucaEcNumbers:
                if lucaEC.contains(nukaEC):
                    nukaEcContainedInLuca = True
                    break
            
            if nukaEcContainedInLuca == False: # NUKA's EC number is not contained in any of LUCA'S EC numbers
                graph.removeEcEdge(substrate, product, nukaEC, bothDirections = False) # remove this edge, both directions will be removed eventually
        
        graph.name = 'Substrate-EC GoldmanLUCA'
        
        # remove isolated nodes
        graph.removeIsolatedNodes()
        
        if init_verbosity > 0:
            print('calculated ' + graph.name)
        
        return graph
    
    
    


class KeggLUCA(object):

    class CladeType(Enum):
        universal = "/"
        archaea = "/Archaea"
        bacteria = "/Bacteria"
        eukaryota = "/Eukaryota"
        archaeaBacteria = [archaea, bacteria]
        archaeaEukaryota = [archaea, eukaryota]
        bacteriaEukaryota = [bacteria, eukaryota]
    
    def __init__(self, clade: 'KeggLUCA.CladeType'):
        """
        !!! WARNING !!! This function takes hours to days to complete, and requires several gigabytes of memory, disk space, and network traffic!
        This is the Last Universal Common Ancestor, as defined by a common 'core' metabolism shared among all organisms known to KEGG within a certain NCBI top-clade.
        This would include Bacteria, Arachaea, and Eukaryota; which is a very big data set!
        Alternatively, you can specify which isolated top-clade to use, using 'clade', e.g. yielding the Bacteria-LUCA, or Archaea-LUCA.
        
        Conversion into another type of graph is not supported, because LUCA is a strictly hypothetical organism without any exactly known genes.
        !!! WARNING !!! This function takes hours to days to complete, and requires several gigabytes of memory, disk space, and network traffic!
        """
        if not isinstance(clade, self.CladeType):
            raise ValueError("No valid top-clade of type KeggLUCA.CladeType specified")
        self.cladeType = clade 
        
        if clade == self.CladeType.universal:
            self.nameAbbreviation = 'Universal-KeggLUCA'
            self.clade = self._getUniversalClade()
        
        elif clade == self.CladeType.archaea:
            self.nameAbbreviation = 'Archaea-KeggLUCA'
            self.clade = self._getArchaeaClade()
        
        elif clade == self.CladeType.bacteria:
            self.nameAbbreviation = 'Bacteria-KeggLUCA'
            self.clade = self._getBacteriaClade()
            
        elif clade == self.CladeType.eukaryota:
            self.nameAbbreviation = 'Eukaryota-KeggLUCA'
            self.clade = self._getEukaryotaClade()
            
        elif clade == self.CladeType.archaeaBacteria:
            self.nameAbbreviation = 'Archaea-Bacteria-KeggLUCA'
            self.clade = self._getArchaeaBacteriaClade()
            
        elif clade == self.CladeType.archaeaEukaryota:
            self.nameAbbreviation = 'Archaea-Eukaryota-KeggLUCA'
            self.clade = self._getArchaeaEukaryotaClade()
            
        elif clade == self.CladeType.bacteriaEukaryota:
            self.nameAbbreviation = 'Bacteria-Eukaryota-KeggLUCA'
            self.clade = self._getBacteriaEukaryotaClade()
            
        else:
            raise ValueError("Unkown KeggLUCA.CladeType")
    
    @cache('KeggLUCA/graph', 'universal_clade')
    def _getUniversalClade(self):
        return self._getClade(self.CladeType.universal.value)
    
    @cache('KeggLUCA/graph', 'archaea_clade')
    def _getArchaeaClade(self):
        return self._getClade(self.CladeType.archaea.value)
    
    @cache('KeggLUCA/graph', 'bacteria_clade')
    def _getBacteriaClade(self):
        return self._getClade(self.CladeType.bacteria.value)
    
    @cache('KeggLUCA/graph', 'eukaryota_clade')
    def _getEukaryotaClade(self):
        return self._getClade(self.CladeType.eukaryota.value)
    
    @cache('KeggLUCA/graph', 'archaea_bacteria_clade')
    def _getArchaeaBacteriaClade(self):
        return self._getClade(self.CladeType.archaeaBacteria.value)
    
    @cache('KeggLUCA/graph', 'archaea_eukaryota_clade')
    def _getArchaeaEukaryotaClade(self):
        return self._getClade(self.CladeType.archaeaEukaryota.value)
    
    @cache('KeggLUCA/graph', 'bacteria_eukaryota_clade')
    def _getBacteriaEukaryotaClade(self):
        return self._getClade(self.CladeType.bacteriaEukaryota.value)
    
    def _getClade(self, ncbiName):
        clade = FEV_KEGG.Evolution.Clade.Clade(ncbiName)
        clade.collectiveMetabolism(noMultifunctional=False)
        return clade
    
    
    def substrateEcGraph(self, majorityPercentage) -> SubstrateEcGraph:
        graph = self.clade.coreMetabolism(majorityPercentage=majorityPercentage, noMultifunctional=False)
        graph.removePartialEcNumbers()
        graph.removeIsolatedNodes()
        graph.name = 'Substrate-EC ' + self.nameAbbreviation
        return graph
        