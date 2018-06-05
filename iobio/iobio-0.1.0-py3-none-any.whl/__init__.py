from sklearn.cluster import AgglomerativeClustering
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import zscore
#from collections import namedtuple
#OrderedCluster = namedtuple('OrderedCluster',['ids','colors'])
def cluster_ordered_agglomerative (dataframe,
	                               n_clusters=2,
	                               affinity='euclidean',
	                               memory=None,
	                               connectivity=None,
	                               compute_full_tree='auto',
	                               linkage='ward',
	                               rankstat='median',
	                               cmapcolors='Blues',
                                       z_score=False):
    if z_score: dataframe = dataframe.copy().apply(zscore)
    clusters = AgglomerativeClustering(n_clusters=n_clusters,
    	                               affinity=affinity,
    	                               memory=memory,
    	                               connectivity=connectivity,
    	                               compute_full_tree=compute_full_tree,
    	                               linkage=linkage).\
        fit_predict(dataframe)
    clusters = pd.DataFrame({'unordered_id':clusters})
    clusters.index = dataframe.index
    rowsums = pd.DataFrame(dataframe.sum(1)).rename(columns={0:'rankstat'})
    clusters = clusters.merge(rowsums,left_index=True,right_index=True)
    rankfunc = None
    if rankstat == 'median': rankfunc = np.median
    elif rankstat == 'mean': rankfunc = np.mean
    else: raise ValueError("unsupported rankstat: "+str(rankstat))
    ordered = list(clusters.groupby('unordered_id').\
    	apply(lambda x: rankfunc(x['rankstat'])).sort_values().index)
    converter = dict(zip(ordered,range(0,n_clusters)))
    cluster_ids = clusters.apply(lambda x: converter[x['unordered_id']],1)
    clusters['cluster_id'] = cluster_ids
    colorconverter = sns.color_palette(cmapcolors,n_clusters)
    cluster_colors = clusters.apply(lambda x: colorconverter[int(x['cluster_id'])],1)
    clusters['cluster_colors'] = cluster_colors

    ordered_index = clusters.sort_values(['cluster_id','rankstat']).index
    dfo = pd.DataFrame({'ordered_index':ordered_index})
    dfo['order_index'] = range(0,dfo.shape[0])
    dfo = dfo.set_index('ordered_index')
    saveindex = clusters.index
    clusters = clusters.merge(dfo,left_index=True,right_index=True)
    clusters = clusters.loc[saveindex]
    return clusters.drop(columns=['unordered_id'])
