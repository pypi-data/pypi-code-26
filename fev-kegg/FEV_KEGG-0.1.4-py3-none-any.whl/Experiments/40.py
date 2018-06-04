"""
Question
--------
When comparing the core metabolism of Archaea and Gammaproteobacteria, what differences and similarities occur?

Method
------
- build Archaea -> Gammaproteobacteria clade pair
- export coloured graph to file, containing all three sets of differing ECs, using the default majority percentage of 80
- REPEAT for varying majority-percentages:
-     overlap sets and print amount of EC numbers inside the intersection and falling off either side
-     remove wildcard EC numbers

Result
------

::

    Maj. % Archaea  both  Gammap.
    100%:      6      2      0
    90%:     35     51    139
    80%:     36     88    188
    70%:     46    122    191
    60%:     56    136    223
    50%:     72    169    255
    40%:     81    191    296
    30%:    101    227    349
    20%:    105    273    400
    10%:    135    366    433
    1%:    144    607    481


Conclusion
----------
Regarding 100% majority, it is obvious that neither Archaea, nor Gammaproteobacteria have a significant consensus in themselves, leaving no room for a significant consensus between them.
It might be noted that Archaea seem to tend to have a bigger consensus, 8 vs. 2, but then they have only quarter of the organisms the Gammaproteobacteria consist of.
What this does show, however, is that both taxa possess a great varity of metabolic capabilities, or at least a lack of complete data sets.

Regarding the span between 90% and 10% majority, the amount of ECs added in either category grow almost linearly, with a slight exponential tendency, but equally distributed between the three sets.

Regarding the jump from 10% to 1%, it shows that both groups suddenly share almost double the ECs, without adding much more to their only set.
This might ordinarily mean that both groups are equally diversified in metabolic function and they use most functions known to nature.

However, this could also be evidence of horizontal gene transfer rarely occuring between small numbers of archaea and gammaproteobacteria strains.
To further research this idea, one would have to extract the ECs occuring only in a few archaea/gammaproteobacteria (~1% majority). Then for each EC, find the encoding enzymes, grouped by archaea and gammaproteobacteria.
Then, find out how many of these enzymes, sharing the same EC but belonging to different groups, have orthologous genes. If there is a significant amount of these, it is proof of relatively abundant horizontal gene transfer for rare metabolic functions.
"""
from FEV_KEGG.Evolution.Clade import Clade, CladePair
from FEV_KEGG.KEGG.File import cache
from FEV_KEGG.Graph.Elements import EcNumber
from FEV_KEGG.Drawing import Export

@cache(folder_path = 'experiments/40/', file_name = 'archaea_clade')
def getArchaeaClade():
    clade = Clade('/Archaea')
    # pre-fetch collective metabolism into memory
    clade.collectiveMetabolism(excludeMultifunctionalEnzymes = True)
    return clade

@cache(folder_path = 'experiments/40/', file_name = 'gammaproteobacteria_clade')
def getGammaproteobacteriaClade():
    clade = Clade('Proteobacteria/Gammaproteobacteria')
    # pre-fetch collective metabolism into memory
    clade.collectiveMetabolism(excludeMultifunctionalEnzymes = True)
    return clade
    
if __name__ == '__main__':
    
    output = ['Maj. %\tArchaea\tboth\tGammap.']
    
    
    #- build Archaea -> Gammaproteobacteria clade pair
    archaea_clade = getArchaeaClade()
    
    gammaproteobacteria_clade = getGammaproteobacteriaClade()
    
    cladePair = CladePair(archaea_clade, gammaproteobacteria_clade)
    
    #- export coloured graph to file, containing all three sets of differing ECs, using the default majority percentage of 80
    cladePair_graph = cladePair.unifiedMetabolism(colour = True)
    Export.forCytoscape(cladePair_graph, 'archaea_vs_gammaproteobacteria')
    
    #- REPEAT for varying majority-percentages:
    for percentage in [100, 90, 80, 70, 60, 50, 40, 30, 20, 10 , 1]:
          
        #-     overlap sets and print amount of EC numbers inside the intersection and falling off either side
        only_archaea = cladePair.lostMetabolism(percentage).getECs()
        both = cladePair.conservedMetabolism(percentage).getECs()
        only_gammaproteobacteria = cladePair.addedMetabolism(percentage).getECs()
         
        #-     remove wildcard EC numbers
        only_archaea = EcNumber.removeWildcards(only_archaea)
        both = EcNumber.removeWildcards(both)
        only_gammaproteobacteria = EcNumber.removeWildcards(only_gammaproteobacteria)
          
        output.append(str(percentage) + '%:\t' + str(len(only_archaea)) + '\t' + str(len(both)) + '\t' + str(len(only_gammaproteobacteria)) )
         
    for line in output:
        print(line)
