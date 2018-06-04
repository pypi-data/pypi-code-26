"""
Question
--------
Which enzymes, independent from substrate/product, are present in eco00260, but not in eco01100?

Method
------
- Download pathway definition as KGML.
- Convert to substrate-reaction graph.
- Convert to substrate-gene graph.
- Convert to substrate-enzyme graph
- Get set of enzymes for each graph.
- Calculate difference of enzyme sets.
- Print enzymes (gene name, enzyme name, all associated EC numbers, enzyme long name).

Result
------

::

    3 results
    b2366 dsdA [4.3.1.18] D-serine dehydratase
    b3616 tdh [1.1.1.103] threonine 3-dehydrogenase
    b3617 kbl [2.3.1.29] glycine C-acetyltransferase


Conclusion
----------
Global map 01100 does not necessarily contain all enzymes for an organism.
"""
from FEV_KEGG.Graph.SubstrateGraphs import SubstrateReactionGraph, SubstrateGeneGraph, SubstrateEnzymeGraph
from FEV_KEGG.KEGG.Organism import Organism


if __name__ == '__main__':
    
    #- Download pathway definition as KGML.
    eco = Organism('eco')
    
    eco00260 = eco.getPathway('00260')
    eco01100 = eco.getPathway('01100')
    
    #- Convert to substrate-reaction graph.
    eco00260_reactionGraph = SubstrateReactionGraph.fromPathway(eco00260)
    eco01100_reactionGraph = SubstrateReactionGraph.fromPathway(eco01100)
    
    #- Convert to substrate-gene graph
    eco00260_geneGraph = SubstrateGeneGraph.fromSubstrateReactionGraph(eco00260_reactionGraph)
    eco01100_geneGraph = SubstrateGeneGraph.fromSubstrateReactionGraph(eco01100_reactionGraph)
    
    #- Convert to substrate-enzyme graph
    eco00260_enzymeGraph = SubstrateEnzymeGraph.fromSubstrateGeneGraph(eco00260_geneGraph)
    eco01100_enzymeGraph = SubstrateEnzymeGraph.fromSubstrateGeneGraph(eco01100_geneGraph)
    
    #- Get set of enzymes for each graph.
    eco00260_enzymes = eco00260_enzymeGraph.getEnzymes()
    eco01100_enzymes = eco01100_enzymeGraph.getEnzymes()
    
    #- Calculate difference of enzyme sets.
    difference_enzymes = eco00260_enzymes.difference(eco01100_enzymes)
    
    #- Print enzymes (gene name, enzyme name, all associated EC numbers, enzyme long name).
    output = []
    for enzyme in difference_enzymes:
        output.append(enzyme.geneName + ' ' + enzyme.name + ' [' + enzyme.getEcNumbersString() + '] ' + enzyme.definition)
    output.sort()
    print(str(len(output)) + ' results')
    for line in output:
        print(line)