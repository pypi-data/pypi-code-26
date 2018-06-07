# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 10:02:44 2015

@author: dominic
"""
#__package__ = 'pylogenetics'

import pandas as pd, numpy as np

def contrasts_uppass(tree, node, vcv, node_to_tip):
    print "Up-pass at node", node
    descs=tree.successors(node)
    tips_of_descs = []
    node_to_tip[node] = {}
    for desc in descs:
        print " Descendents:", desc
        if tree.degree(desc)==1:
            tips_of_descs.append([desc])
            node_to_tip[node][desc]=tree.edge[node][desc]['length']
        else:
            contrasts_uppass(tree, desc, vcv, node_to_tip)
            tips_of_descs.append(node_to_tip[desc].keys())
            for t in node_to_tip[desc].keys():
                node_to_tip[node][t]=node_to_tip[desc][t]+tree.edge[node][desc]['length']
    for desc in descs:
        all_tips = sorted(tree.tip_keys())
        for idx, tips in enumerate(tips_of_descs):
            if idx == len(tips_of_descs)-1:
                break
            for tips2 in tips_of_descs[idx+1:]:
                for t1 in tips:
                    i1 = all_tips.index(t1)
                    for t2 in tips2:
                        i2 = all_tips.index(t2)
                        l = node_to_tip[node][t1]+node_to_tip[node][t2]
                        vcv[i1,i2] = l
                        vcv[i2,i1] = l

def contrasts_downpass(tree, node, vcv, node_to_tip):
    print "Downpass at node", node
    tips_of_descs = []
    descs=tree.successors(node)
    if len(descs)==0:
        node_to_tip[tree.predecessors(node)[0]]={node:tree.edge[tree.predecessors(node)[0]][node]['length']}
    else:
        if node not in node_to_tip.keys():
            node_to_tip[node]={}
        for desc in descs:
            print " Descendents:"
            if desc in node_to_tip[node]:
                print '  ', desc, 'already visited'
                if tree.degree(desc)==1:
                    tips_of_descs.append([desc])
                    node_to_tip[node][desc]=tree.edge[node][desc]['length']
                else:
                    tips_of_descs.append(node_to_tip[desc].keys())
                    for t in node_to_tip[desc].keys():
                        node_to_tip[node][t]=node_to_tip[desc][t]+tree.edge[node][desc]['length']
            else:
                print '  ', desc, "not visited"
                contrasts_uppass(tree, desc, vcv, node_to_tip)
                tips_of_descs.append(node_to_tip[desc].keys())
                for t in node_to_tip[desc].keys():
                    node_to_tip[node][t]=node_to_tip[desc][t]+tree.edge[node][desc]['length']
        all_tips = sorted(tree.tip_keys())
        for idx, tips in enumerate(tips_of_descs):
            if idx == len(tips_of_descs)-1:
                break
            for tips2 in tips_of_descs[idx+1:]:
                for t1 in tips:
                    i1 = all_tips.index(t1)
                    for t2 in tips2:
                        i2 = all_tips.index(t2)
                        l = node_to_tip[node][t1]+node_to_tip[node][t2]
                        vcv[i1,i2] = l
                        vcv[i2,i1] = l
    print "  tips", tips_of_descs
    if tree.degree(node)==2:
        ### Make diagonal of vcv
        all_tips = sorted(tree.tip_keys())
        for t in node_to_tip[node].keys():
            i = all_tips.index(t)
            vcv[i,i] = 2*node_to_tip[node][t]
        return
    else:
        contrasts_downpass(tree, tree.predecessors(node)[0], vcv, node_to_tip)

def contrasts(tree):
    tips = sorted(tree.tip_keys())
    vcv = np.zeros((len(tips),len(tips)))
    print vcv, '\n'
    all_dists = {}
    counter = 0
    start_tip = tips[0]
    start_tip_anc = tree.predecessors(start_tip)[0]
    all_dists[start_tip_anc]={start_tip:tree.edge[start_tip_anc][start_tip]['length']}
    print start_tip
    print vcv
    contrasts_downpass(tree, start_tip, vcv, all_dists)
    
    print "\nFinal"
    print all_dists
    print vcv




def covar_uppass(tree, vcv, node, node_descs, node_heights, all_tips):
    descs = tree.successors(node)
    node_desc_tips = []
    for desc in descs:
        node_heights[desc]=node_heights[node]+tree.edge[node][desc]['length']
        if tree.degree(desc)==1:
            node_desc_tips.append([desc])
            i = all_tips.index(desc)
            vcv[i,i] = node_heights[desc]
        else:
            node_desc_tips.append(covar_uppass(tree,vcv,desc,node_descs,node_heights,all_tips))
    combined_tips = []
    for idx, tips1 in enumerate(node_desc_tips):
        combined_tips+=tips1
        if idx == len(node_desc_tips)-1:
            break
        for tips2 in node_desc_tips[idx+1:]:
            for t1 in tips1:
                i1 = all_tips.index(t1)
                for t2 in tips2:
                    i2 = all_tips.index(t2)
                    l = node_heights[node]
                    vcv[i1,i2] = l
                    vcv[i2,i1] = l
    node_descs[node]=combined_tips
    return combined_tips

def covariance_matrix(tree):
    root = tree.root()
    all_tips = sorted(tree.tip_keys())
    vcv = np.zeros((len(all_tips),len(all_tips)))
    heights = {root:0}
    descendents = {}
    covar_uppass(tree, vcv, root, descendents, heights, all_tips)

def pgls(tree, X, y):
    print "starting pgls"
    print tree.edges()
    print X
    print y, '\n'
#    covariance_matrix(tree)
    
    all_tips = sorted(tree.tip_keys())
    print X.index
    X['new_col'] = pd.Series(np.zeros(3), index=X.index)
    print X
    
    print '\n\n\n'
    print tree.tip_names_dict()
    print 
    return 1




def test():
    from Tree import Tree
    taxa = ['Trex','Triceratops','Stegosaurus']
    meas = [[1,2],[3,2],[3,4]]
    data = pd.DataFrame(meas, taxa)
    test_tree = Tree()
    test_tree.add_edges_from(((0,1),(0,2),(2,3),(2,4)))
    for e in test_tree.edges():
        test_tree.edge[e[0]][e[1]]['length']=1
    test_tree.add_tip_names({1:'Trex',
                             3:'Triceratops',
                             4:'Stegosaurus'})
    pgls(test_tree,data.iloc[:,0],data.loc[:,1])
#    print data.columns()
    return
    

test()