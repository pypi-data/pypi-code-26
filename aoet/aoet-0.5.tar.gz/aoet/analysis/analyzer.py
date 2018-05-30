from aoet import logger, BODY_MATRIX, UNIQUES_LIST
import aoet.report.generator as generator
import aoet.analysis.pca as pca

import sklearn.cluster as cluster

import pandas as pd
import numpy as np
import json
import os


def clusterize(X, epsilon, n_jobs):
    """
    Performs DBSCAN for provided matrix.
    
    :param X: Input matrix
    :param epsilon: input parameter for DBSCAN
    :param n_jobs: Number of parallel jobs to run
    :return: 
    
    Reference
    ----------
    http://scikit-learn.org/stable/auto_examples/cluster/plot_dbscan.html#sphx-glr-auto-examples-cluster-plot-dbscan-py
    """
    min_samples = 10
    logger.info('Performing DBSCAN with eps={} and min_samples={}'.format(epsilon, min_samples))

    db = cluster.DBSCAN(eps=epsilon, min_samples=min_samples, n_jobs=n_jobs).fit(X)

    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    outliers = len(labels[labels == -1])

    logger.info('DBSCAN returned {} clusters and {} outliers'.format(n_clusters, outliers))

    return labels, core_samples_mask, n_clusters, outliers


def generate(arguments):
    if arguments.raw_dir is None:
        arguments.raw_dir = arguments.in_dir

    with open(os.path.join(arguments.in_dir, UNIQUES_LIST)) as fp:
        uniques = np.array(json.load(fp))

    frame = pd.read_csv(os.path.join(arguments.in_dir, BODY_MATRIX))
    if frame.shape[1] > 3:
        dim2 = pca.pca_projection(frame.values[:, 1:], 2)
    else:
        dim2 = frame.values[:, 1:]

    labels, core, n_clusters, outliers = clusterize(dim2, float(arguments.epsilon), arguments.n_jobs)

    core_samples = []

    for k in range(n_clusters):
        m = (labels == k) & core
        for i in range(len(m)):
            if m[i]:
                core_samples.append(i)
                break

    generator.to_report(dim2, arguments.raw_dir, uniques, arguments.out, labels, core_samples, n_clusters, outliers)



def add_subparsers(subparsers):
    parser_a = subparsers.add_parser('report', help='Produces final report')

    parser_a.add_argument('--in',  dest='in_dir', type=str, default='out', required=True, help='Location of converted matrix')
    parser_a.add_argument('--raw', dest='raw_dir', type=str, default=None, help='Location of raw requests. By default is'
                                                                                ' assumed to be equal to input directory')
    parser_a.add_argument('--epsilon',  dest='epsilon',  type=float, default=0.035, help='Epsilon value for DBSCAN')
    parser_a.add_argument('--out', '-o', dest='out', type=str, default='report', help='Folder for the final report')
    parser_a.add_argument('--jobs', dest='n_jobs', type=int, default=-1, help='Number of parallel jobs to run')
    parser_a.set_defaults(func=generate)


if __name__ == '__main__':
    from argparse import Namespace
    n = Namespace()
    n.in_dir = '../../../data/real1_real2'
    n.out = '../../../reports/real1_real2'

    n.raw_dir = None
    n.epsilon = 0.035
    n.n_jobs = -1

    generate(n)