"""
Question
--------
Which EC numbers, independent from substrate/product, are present in eco00260, but not in eco01100?

Method
------
- Download pathway description as KGML.
- Convert to substrate-reaction graph.
- Convert to substrate-gene graph.
- Convert to substrate-ec graph
- Get set of EC numbers for each graph.
- Calculate difference of EC number sets.
- Print genes (EC number).

Result
------

::

    3 results
    1.1.1.103
    2.3.1.29
    4.3.1.18


Conclusion
----------
Global map 01100 does not necessarily contain all EC numbers for an organism.
"""
from FEV_KEGG.Graph.SubstrateGraphs import SubstrateReactionGraph, SubstrateGeneGraph, SubstrateEcGraph
from FEV_KEGG.KEGG.Organism import Organism


if __name__ == '__main__':
    
    #- Download pathway description as KGML.
    eco = Organism('eco')
    
    eco00260 = eco.getPathway('00260')
    eco01100 = eco.getPathway('01100')
    
    #- Convert to substrate-reaction graph.
    eco00260_reactionGraph = SubstrateReactionGraph.fromPathway(eco00260)
    eco01100_reactionGraph = SubstrateReactionGraph.fromPathway(eco01100)
    
    #- Convert to substrate-gene graph
    eco00260_geneGraph = SubstrateGeneGraph.fromSubstrateReactionGraph(eco00260_reactionGraph)
    eco01100_geneGraph = SubstrateGeneGraph.fromSubstrateReactionGraph(eco01100_reactionGraph)
    
    #- Convert to substrate-ec graph
    eco00260_ecGraph = SubstrateEcGraph.fromSubstrateGeneGraph(eco00260_geneGraph)
    eco01100_ecGraph = SubstrateEcGraph.fromSubstrateGeneGraph(eco01100_geneGraph)
    
    #- Get set of EC numbers for each graph.
    eco00260_ecNumbers = eco00260_ecGraph.getECs()
    eco01100_ecNumbers = eco01100_ecGraph.getECs()
    
    #- Calculate difference of EC number sets.
    difference_ecNumbers = eco00260_ecNumbers.difference(eco01100_ecNumbers)
    
    #- Print genes (EC number).
    output = []
    for ecNumber in difference_ecNumbers:
        output.append(ecNumber.__str__())
    output.sort()
    print(str(len(output)) + ' results')
    for line in output:
        print(line)