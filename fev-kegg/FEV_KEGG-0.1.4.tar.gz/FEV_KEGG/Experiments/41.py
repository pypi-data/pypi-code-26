"""
Context
-------
In :mod:`Experiments.40`, we asked whether the big jump of shared EC numbers for a very low majority percentage might be linked with horizontal gene transfer of rare metabolic functions.

Question
--------
When comparing the metabolism of Archaea and Gammaproteobacteria, regarding the functions exclusive to only a few (or even just one) of the organisms, are the enzymes encoding them orthologous between Archaea and Gammaproteobacteria?

Method
------
- build Archaea -> Gammaproteobacteria clade pair
- for varying and low majority-percentages:
-     overlap sets and print amount of EC numbers inside the intersection and falling off either side
-     remove wildcard EC numbers
-     REPEAT for each EC, occuring in both:
-         find encoding enzymes, save them separately for both groups
-         find orthologous enzyme pairs between both groups
-     print count of enzymes in both groups and amount of which are orthologous

Result
------

::

    Maj. % Archaea  both  Gammap.
    


Conclusion
----------

"""
from FEV_KEGG.Evolution.Clade import Clade, CladePair
from FEV_KEGG.KEGG.File import cache
from FEV_KEGG.Graph.Elements import EcNumber
from FEV_KEGG.KEGG import Database

@cache(folder_path = 'experiments/40/', file_name = 'archaea_clade')
def getArchaeaClade():
    clade = Clade('/Archaea')
    # pre-fetch collective metabolism into memory
    clade.collectiveMetabolism(excludeMultifunctionalEnzymes = True)
    clade.collectiveMetabolismEnzymes(excludeMultifunctionalEnzymes = True)
    return clade

@cache(folder_path = 'experiments/40/', file_name = 'gammaproteobacteria_clade')
def getGammaproteobacteriaClade():
    clade = Clade('Proteobacteria/Gammaproteobacteria')
    # pre-fetch collective metabolism into memory
    clade.collectiveMetabolism(excludeMultifunctionalEnzymes = True)
    clade.collectiveMetabolismEnzymes(excludeMultifunctionalEnzymes = True)
    return clade
    
if __name__ == '__main__':
    
    output = ['Maj. %\tArchaea\tboth\tGammap.']
    
    
    #- build Archaea -> Gammaproteobacteria clade pair
    archaea_clade = getArchaeaClade()
    
    gammaproteobacteria_clade = getGammaproteobacteriaClade()
    
    cladePair = CladePair(archaea_clade, gammaproteobacteria_clade)
    
    archaea_enzymes = archaea_clade.collectiveMetabolismEnzymes()
    gammaproteobacteria_enzymes = gammaproteobacteria_clade.collectiveMetabolismEnzymes()
    
    #- REPEAT for varying low majority-percentages:
    for percentage in [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0.1, 0.01]:
        #TODO: nur die ECs untersuchen die neu dazugekommen sind!
        #-     overlap sets and print amount of EC numbers inside the intersection and falling off either side
        only_archaea = cladePair.lostMetabolism(percentage).getECs()
        both = cladePair.conservedMetabolism(percentage).getECs()
        only_gammaproteobacteria = cladePair.addedMetabolism(percentage).getECs()
         
        #-     remove wildcard EC numbers
        only_archaea = EcNumber.removeWildcards(only_archaea)
        both = EcNumber.removeWildcards(both)
        only_gammaproteobacteria = EcNumber.removeWildcards(only_gammaproteobacteria)
          
        output.append(str(percentage) + '%:\t' + str(len(only_archaea)) + '\t' + str(len(both)) + '\t' + str(len(only_gammaproteobacteria)) )
        
        #-     REPEAT for each EC, occuring in both:
        
        bla = 0
        bla2 = 0
        
        for ec in both:
            
            #-         find encoding enzymes, save them separately for both groups
            archaea_enzymes_by_ec = archaea_enzymes.getEnzymesForEcNumber(ec)
            gammaproteobacteria_enzymes_by_ec = gammaproteobacteria_enzymes.getEnzymesForEcNumber(ec)
            
            bla += len(gammaproteobacteria_enzymes_by_ec)
            bla2 += len(archaea_enzymes_by_ec)
            
            #-         find orthologous enzyme pairs between both groups
            #TODO: Evolution.Comparison machen
        
        output.append(bla)
        output.append(bla2)
        
        #-     print count of enzymes in both groups and amount of which are orthologous
         
    for line in output:
        print(line)
