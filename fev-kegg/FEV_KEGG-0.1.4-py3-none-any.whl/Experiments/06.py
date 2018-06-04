"""
Question
--------
Which genes, independent from substrate/product, are present in eco00260, but not in eco01100?

Method
------
- Download pathway description as KGML.
- Convert to substrate-reaction graph.
- Convert to substrate-gene graph.
- Get set of genes for each graph.
- Calculate difference of gene sets.
- Print genes (gene ID).

Result
------

::

    3 results
    eco:b2366
    eco:b3616
    eco:b3617


Conclusion
----------
Global map 01100 does not necessarily contain all enzyme-coding genes for an organism.
"""
from FEV_KEGG.Graph.SubstrateGraphs import SubstrateReactionGraph, SubstrateGeneGraph
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
    
    #- Get set of genes for each graph.
    eco00260_genes = eco00260_geneGraph.getGenes()
    eco01100_genes = eco01100_geneGraph.getGenes()
    
    #- Calculate difference of gene sets.
    difference_genes = eco00260_genes.difference(eco01100_genes)
    
    #- Print genes (gene ID).
    output = []
    for gene in difference_genes:
        output.append(gene.__str__())
    output.sort()
    print(str(len(output)) + ' results')
    for line in output:
        print(line)