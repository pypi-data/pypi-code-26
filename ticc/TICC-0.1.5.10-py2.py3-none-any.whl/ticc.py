import csv
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD, PCA
import logging
from collections import namedtuple
import concurrent.futures as cf
import threading
from multiprocessing import Pool
import multiprocessing

import math, time, collections, os, errno, sys, code, random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from scipy import stats

from sklearn import mixture, covariance
from sklearn.cluster import KMeans
import pandas as pd

import logging


GlobalPool=None
PoolLock = threading.Lock()


#######################################################################################################################################################################
pd.set_option('display.max_columns', 500)
np.set_printoptions(formatter={'float': lambda x: "{0:0.4f}".format(x)})
np.random.seed(102)

####################################################################################################################################################################################################


# Problem Instance. Contains fields for problem except for the BIC
# changeable ones.
ProblemInstance = namedtuple('ProblemInstance',
                             ['input_data', 'window_size', 'maxIters', 'threshold'])

def RunTicc(input_filename, output_filename, cluster_number=range(2, 11), process_pool_size=10,
            window_size=1, lambda_param=[1e-2], beta=[0.01, 0.1, 0.5, 10, 50, 100, 500],
            maxIters=1000, threshold=2e-5, covariance_filename=None,
            input_format='matrix', delimiter=',', BIC_Iters=15, input_dimensions=50,
            logging_level=logging.INFO):
    '''
    Required Parameters:
    -- input_filename: the path to the data file. see input_format below
    -- output_filename: the output file name to write the cluster assignments

    Optional Parameters: BIC
    For each of these parameters, one can choose to specify:
        - a single number: this value will be used as the parameter
        - a list of numbers: the solver will use grid search on the BIC to choose the parameter
        - not specified: the solver will grid search on a default range (listed) to choose the parameter
    -- cluster_number: The number of clusters to classify. Default: BIC on [2...10]
    -- lambda_param: sparsity penalty. Default: BIC on 11e-2]
    -- beta: the switching penalty. If not specified, BIC on [50, 100, 200, 400]

    Other Optional Parameters:
    -- input_dimensions: if specified, will truncated SVD the matrix to the given number of features
       if the input is a graph, or PCA it if it's a matrix
    -- BIC_iters: if specified, will only run BIC tuning for the given number of iterations
    -- process_pool_size: the number of processes to spin off for optimization. Default 1
    -- window_size: The size of the window for each cluster. Default 1
    -- maxIters: the maximum number of iterations to allow TICC to run. Default 1000
    -- threshold: the convergence threshold. Default 2e-5
    -- covariance_filename: if not None, write the covariance into this file
    -- file_type is the type of data file. the data file must 
       be a comma separated CSV. the options are:
       -- "matrix": a numpy matrix where each column is a feature and each
          row is a time step
       -- "graph": an adjacency list with each row having the form:
          <start label>, <end label>, value
    -- delimiter is the data file delimiter
    '''
    logging.basicConfig(level=logging_level)
    input_data = None
    if input_format == 'graph':
        input_data = retrieveInputGraphData(
            input_filename, input_dimensions, delim=delimiter)
    elif input_format == "matrix":
        input_data = np.loadtxt(input_filename, delimiter=delimiter)
        if input_dimensions is not None and input_dimensions < np.shape(input_data)[1]:
            pca = PCA(n_components=input_dimensions)
            input_data = pca.fit_transform(input_data)

    else:
        raise ValueError("input_format must either be graph or matrix")

    logging.debug("Data loaded! With shape %s, %s" % (
        np.shape(input_data)[0], np.shape(input_data)[1]))

    # get params via BIC
    cluster_number = cluster_number if isinstance(
        cluster_number, list) else [cluster_number]
    beta = beta if isinstance(beta, list) else [beta]
    lambda_param = lambda_param if isinstance(
        lambda_param, list) else [lambda_param]
    BIC_Iters = maxIters if BIC_Iters is None else BIC_Iters
    problem_instance = ProblemInstance(input_data=input_data, window_size=window_size,
                                       maxIters=BIC_Iters, threshold=threshold)
    clusterResults = runHyperParameterTuning(beta, lambda_param, cluster_number,
                                             process_pool_size, problem_instance)
    final_results = []
    for cluster_number, resultPackage in clusterResults:
        params, results, score = resultPackage
        beta, lambda_param = params
        logging.info("Via BIC with score %s, using params beta: %s, clusterNum %s, lambda %s" % (
            score, beta, cluster_number, lambda_param))
        # perform real run
        cluster_assignments, cluster_MRFs = (None, None)
        if BIC_Iters == maxIters:  # already performed the full run
            cluster_assignments, cluster_MRFs = results
        else:
            (cluster_assignment, cluster_MRFs) = solve(
                window_size=window_size, number_of_clusters=cluster_number, lambda_parameter=lambda_param,
                beta=beta, maxIters=maxIters, threshold=threshold,
                input_data=input_data, num_processes=process_pool_size, logging_level=logging_level)
        outstream = "%s_%s" % (cluster_number, output_filename)
        np.savetxt(outstream, cluster_assignment, fmt='%d', delimiter=',')
        final_results.append(
            (cluster_assignment, cluster_MRFs, (beta, lambda_param, cluster_number)))
    return final_results


def GetChangePoints(cluster_assignment):
    '''
    Pass in the result of RunTicc to split into changepoint indexes
    '''
    currIndex = -1
    index = -1
    currCluster = -1
    results = []
    for cluster in cluster_assignment:
        if currCluster != cluster:
            if currCluster != -1:
                results.append((currIndex, index, currCluster))
            index += 1
            currIndex = index
            currCluster = cluster
        else:
            index += 1
    results.append((currIndex, index, currCluster))
    return results


def retrieveInputGraphData(input_filename, input_dimensions, delim=','):
    mapping = {}  # edge to value
    sparse_cols = []  # list of indices that should be 1

    with open(input_filename, 'r') as csvfile:
        datareader = csv.reader(csvfile, delimiter=delim, quotechar='|')
        counter = 0
        curr_timestamp = None
        for row in datareader:
            key = "%s_%s" % (row[0], row[1])
            timestamp = row[2]
            if timestamp != curr_timestamp:  # new time
                curr_timestamp = timestamp
                sparse_cols.append(set())
            if key not in mapping:  # a new feature
                # assign this key to the current counter value
                mapping[key] = counter
                counter += 1
            # assign this feature into the current time step
            sparse_cols[-1].add(mapping[key])

    lenRow = len(mapping.keys())
    if input_dimensions is None or lenRow <= input_dimensions:  # do not need to SVD
        rows = []
        for indices in sparse_cols:
            # indices is a set
            row = [1.0 if i in indices else 0.0 for i in range(lenRow)]
            rows.append(row)
        return np.array(rows)
    else:
        # need to truncated svd
        data = []
        rows = []
        cols = []
        for i, indices in enumerate(sparse_cols):  # row
            for j in range(lenRow):  # col
                if j in indices:
                    data.append(1)
                    rows.append(i)
                    cols.append(j)
        mat = csr_matrix((data, (rows, cols)),
                         shape=(len(sparse_cols), lenRow))
        solver = TruncatedSVD(n_components=input_dimensions)
        return solver.fit_transform(mat)


def runHyperParameterTuning(beta_vals, lambda_vals, cluster_vals,
                            process_pool_size, problem_instance):
    num_runs = len(beta_vals)*len(lambda_vals)
    pool = Pool(processes=process_pool_size)
    futures = []
    for i, c in enumerate(cluster_vals):
        future_list = []
        for l in lambda_vals:
            for b in beta_vals:
                future_list.append(pool.apply_async(
                    runBIC, (b, c, l, problem_instance,)))
        futures.append(future_list)
    # retrieve results
    # [cluster, (bestParams, bestResults, bestScore)]
    results = []
    for i, c in enumerate(cluster_vals):
        bestParams = (0, 0)  # beta, cluster, lambda
        bestResults = (None, None)
        bestScore = None
        bestConverge = False
        for j in range(num_runs):
            vals = futures[i][j].get()
            clusts, mrfs, score, converged, params = vals
            logging.info("%s,%s,%s" % (cluster_vals[i], params, score))
            if bestScore is None or (converged >= bestConverge and score < bestScore):
                bestScore = score
                bestParams = params
                bestResults = (clusts, mrfs)
                bestConverge = converged
        resultPackage = (bestParams, bestResults, bestScore)
        results.append((cluster_vals[i], resultPackage))
    pool.close()
    pool.join()
    return results


def runBIC(beta, cluster, lambd, pi):
    ''' pi should be a problem instance '''
    clusts, mrfs, score, converged = solve(input_data=pi.input_data, window_size=pi.window_size,
                                           number_of_clusters=cluster, lambda_parameter=lambd,
                                           beta=beta, maxIters=pi.maxIters, threshold=pi.threshold,
                                           compute_BIC=True, num_processes=1)
    return clusts, mrfs, score, converged, (beta, lambd)



class ADMMSolver:
    def __init__(self, lamb, num_stacked, size_blocks, rho, S, rho_update_func=None):
        self.lamb = lamb
        self.numBlocks = num_stacked
        self.sizeBlocks = size_blocks
        probSize = num_stacked*size_blocks
        self.length = probSize*(probSize+1)/2
        self.x = np.zeros(int(self.length))
        self.z = np.zeros(int(self.length))
        self.u = np.zeros(int(self.length))
        self.rho = float(rho)
        self.S = S
        self.status = 'initialized'
        self.rho_update_func = rho_update_func

    def ij2symmetric(self, i,j,size):
        return (size * (size + 1))/2 - (size-i)*((size - i + 1))/2 + j - i

    def upper2Full(self, a):
        n = int((-1  + np.sqrt(1+ 8*a.shape[0]))/2)  
        A = np.zeros([n,n])
        A[np.triu_indices(n)] = a 
        temp = A.diagonal()
        A = (A + A.T) - np.diag(temp)             
        return A 

    def Prox_logdet(self, S, A, eta):
        d, q = np.linalg.eigh(eta*A-S)
        q = np.matrix(q)
        X_var = ( 1/(2*float(eta)) )*q*( np.diag(d + np.sqrt(np.square(d) + (4*eta)*np.ones(d.shape))) )*q.T
        x_var = X_var[np.triu_indices(S.shape[1])] # extract upper triangular part as update variable      
        return np.matrix(x_var).T

    def ADMM_x(self):    
        a = self.z-self.u
        A = self.upper2Full(a)
        eta = 1/self.rho
        x_update = self.Prox_logdet(self.S, A, eta)
        self.x = np.array(x_update).T.reshape(-1)

    def ADMM_z(self, index_penalty = 1):
        a = self.x + self.u
        probSize = self.numBlocks*self.sizeBlocks
        z_update = np.zeros(int(self.length))

        # TODO: can we parallelize these?
        for i in range(self.numBlocks):
            elems = self.numBlocks if i==0 else (2*self.numBlocks - 2*i)/2 # i=0 is diagonal
            for j in range(self.sizeBlocks):
                startPoint = j if i==0 else 0
                for k in range(startPoint, self.sizeBlocks):
                    locList = [((l+i)*self.sizeBlocks + j, l*self.sizeBlocks+k) for l in range(int(elems))]
                    if i == 0:
                        lamSum = sum(self.lamb[loc1, loc2] for (loc1, loc2) in locList)
                        indices = [self.ij2symmetric(loc1, loc2, probSize) for (loc1, loc2) in locList]
                    else:
                        lamSum = sum(self.lamb[loc2, loc1] for (loc1, loc2) in locList)
                        indices = [self.ij2symmetric(loc2, loc1, probSize) for (loc1, loc2) in locList]
                    pointSum = sum(a[int(index)] for index in indices)
                    rhoPointSum = self.rho * pointSum

                    #Calculate soft threshold
                    ans = 0
                    #If answer is positive
                    if rhoPointSum > lamSum:
                        ans = max((rhoPointSum - lamSum)/(self.rho*elems),0)
                    elif rhoPointSum < -1*lamSum:
                        ans = min((rhoPointSum + lamSum)/(self.rho*elems),0)

                    for index in indices:
                        z_update[int(index)] = ans
        self.z = z_update

    def ADMM_u(self):
        u_update = self.u + self.x - self.z
        self.u = u_update

    # Returns True if convergence criteria have been satisfied
    # eps_abs = eps_rel = 0.01
    # r = x - z
    # s = rho * (z - z_old)
    # e_pri = sqrt(length) * e_abs + e_rel * max(||x||, ||z||)
    # e_dual = sqrt(length) * e_abs + e_rel * ||rho * u||
    # Should stop if (||r|| <= e_pri) and (||s|| <= e_dual)
    # Returns (boolean shouldStop, primal residual value, primal threshold,
    #          dual residual value, dual threshold)
    def CheckConvergence(self, z_old, e_abs, e_rel, verbose):
        norm = np.linalg.norm
        r = self.x - self.z
        s = self.rho * (self.z - z_old)
        # Primal and dual thresholds. Add .0001 to prevent the case of 0.
        e_pri = math.sqrt(self.length) * e_abs + e_rel * max(norm(self.x), norm(self.z)) + .0001
        e_dual = math.sqrt(self.length) * e_abs + e_rel * norm(self.rho * self.u) + .0001
        # Primal and dual residuals
        res_pri = norm(r)
        res_dual = norm(s)
        if verbose:
            # Debugging information to print convergence criteria values
            print('  r:', res_pri)
            print('  e_pri:', e_pri)
            print('  s:', res_dual)
            print('  e_dual:', e_dual)
        stop = (res_pri <= e_pri) and (res_dual <= e_dual)
        return (stop, res_pri, e_pri, res_dual, e_dual)

    #solve
    def __call__(self, maxIters, eps_abs, eps_rel, verbose):
        num_iterations = 0
        self.status = 'Incomplete: max iterations reached'
        for i in range(maxIters):
            z_old = np.copy(self.z)
            self.ADMM_x()
            self.ADMM_z()
            self.ADMM_u()
            if i != 0:
                stop, res_pri, e_pri, res_dual, e_dual = self.CheckConvergence(z_old, eps_abs, eps_rel, verbose)
                if stop:
                    self.status = 'Optimal'
                    break
                new_rho = self.rho
                if self.rho_update_func:
                    new_rho = rho_update_func(self.rho, res_pri, e_pri, res_dual, e_dual)
                scale = self.rho / new_rho
                rho = new_rho
                self.u = scale*self.u

            if verbose:
                # Debugging information prints current iteration #
                print('Iteration %d' % i)
        return self.x




def getTrainTestSplit(m, num_blocks, num_stacked):
    '''
    - m: number of observations
    - num_blocks: window_size + 1
    - num_stacked: window_size
    Returns:
    - sorted list of training indices
    '''
    # Now splitting up stuff
    # split1 : Training and Test
    # split2 : Training and Test - different clusters
    training_percent = 1
    # list of training indices
    training_idx = np.random.choice(
        m-num_blocks+1, size=int((m-num_stacked)*training_percent), replace=False)
    # Ensure that the first and the last few points are in
    training_idx = list(training_idx)
    if 0 not in training_idx:
        training_idx.append(0)
    if m - num_stacked not in training_idx:
        training_idx.append(m-num_stacked)
    training_idx = np.array(training_idx)
    return sorted(training_idx)


def upperToFull(a, eps=0):
        ind = (a < eps) & (a > -eps)
        a[ind] = 0
        n = int((-1 + np.sqrt(1 + 8*a.shape[0]))/2)
        A = np.zeros([n, n])
        A[np.triu_indices(n)] = a
        temp = A.diagonal()
        A = np.asarray((A + A.T) - np.diag(temp))
        return A


def hex_to_rgb(value):
    """Return (red, green, blue) for the color given as #rrggbb."""
    lv = len(value)
    out = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    out = tuple([x/256.0 for x in out])
    return out


def updateClusters(LLE_node_vals, switch_penalty=1):
    """
    Takes in LLE_node_vals matrix and computes the path that minimizes
    the total cost over the path
    Note the LLE's are negative of the true LLE's actually!!!!!

    Note: switch penalty > 0
    """
    (T, num_clusters) = LLE_node_vals.shape
    future_cost_vals = np.zeros(LLE_node_vals.shape)

    # compute future costs
    for i in range(T-2, -1, -1):
        j = i+1
        indicator = np.zeros(num_clusters)
        future_costs = future_cost_vals[j, :]
        lle_vals = LLE_node_vals[j, :]
        for cluster in range(num_clusters):
            total_vals = future_costs + lle_vals + switch_penalty
            total_vals[cluster] -= switch_penalty
            future_cost_vals[i, cluster] = np.min(total_vals)

    # compute the best path
    path = np.zeros(T)

    # the first location
    curr_location = np.argmin(future_cost_vals[0, :] + LLE_node_vals[0, :])
    path[0] = curr_location

    # compute the path
    for i in range(T-1):
        j = i+1
        future_costs = future_cost_vals[j, :]
        lle_vals = LLE_node_vals[j, :]
        total_vals = future_costs + lle_vals + switch_penalty
        total_vals[int(path[i])] -= switch_penalty

        path[i+1] = np.argmin(total_vals)

    # return the computed path
    return path


def find_matching(confusion_matrix):
    """
    returns the perfect matching
    """
    _, n = confusion_matrix.shape
    path = []
    for i in range(n):
        max_val = -1e10
        max_ind = -1
        for j in range(n):
            if j in path:
                pass
            else:
                temp = confusion_matrix[i, j]
                if temp > max_val:
                    max_val = temp
                    max_ind = j
        path.append(max_ind)
    return path


def computeF1Score_delete(num_cluster, matching_algo, actual_clusters, threshold_algo, save_matrix=False):
    """
    computes the F1 scores and returns a list of values
    """
    F1_score = np.zeros(num_cluster)
    for cluster in range(num_cluster):
        matched_cluster = matching_algo[cluster]
        true_matrix = actual_clusters[cluster]
        estimated_matrix = threshold_algo[matched_cluster]
        if save_matrix: np.savetxt("estimated_matrix_cluster=" + str(
            cluster)+".csv", estimated_matrix, delimiter=",", fmt="%1.4f")
        TP = 0
        TN = 0
        FP = 0
        FN = 0
        for i in range(num_stacked*n):
            for j in range(num_stacked*n):
                if estimated_matrix[i, j] == 1 and true_matrix[i, j] != 0:
                    TP += 1.0
                elif estimated_matrix[i, j] == 0 and true_matrix[i, j] == 0:
                    TN += 1.0
                elif estimated_matrix[i, j] == 1 and true_matrix[i, j] == 0:
                    FP += 1.0
                else:
                    FN += 1.0
        precision = (TP)/(TP + FP)
        print("cluster #", cluster)
        print("TP,TN,FP,FN---------->", (TP, TN, FP, FN))
        recall = TP/(TP + FN)
        f1 = (2*precision*recall)/(precision + recall)
        F1_score[cluster] = f1
    return F1_score


def compute_confusion_matrix(num_clusters, clustered_points_algo, sorted_indices_algo):
    """
    computes a confusion matrix and returns it
    """
    seg_len = 400
    true_confusion_matrix = np.zeros([num_clusters, num_clusters])
    for point in range(len(clustered_points_algo)):
        cluster = clustered_points_algo[point]
        num = (int(sorted_indices_algo[point]/seg_len) % num_clusters)
        true_confusion_matrix[int(num), int(cluster)] += 1
    return true_confusion_matrix


def computeF1_macro(confusion_matrix, matching, num_clusters):
    """
    computes the macro F1 score
    confusion matrix : requres permutation
    matching according to which matrix must be permuted
    """
    # Permute the matrix columns
    permuted_confusion_matrix = np.zeros([num_clusters, num_clusters])
    for cluster in range(num_clusters):
        matched_cluster = matching[cluster]
        permuted_confusion_matrix[:, cluster] = confusion_matrix[:, matched_cluster]
     # Compute the F1 score for every cluster
    F1_score = 0
    for cluster in range(num_clusters):
        TP = permuted_confusion_matrix[cluster,cluster]
        FP = np.sum(permuted_confusion_matrix[:,cluster]) - TP
        FN = np.sum(permuted_confusion_matrix[cluster,:]) - TP
        precision = TP/(TP + FP)
        recall = TP/(TP + FN)
        f1 = stats.hmean([precision,recall])
        F1_score += f1
    F1_score /= num_clusters
    return F1_score

def computeBIC(K, T, clustered_points, inverse_covariances, empirical_covariances):
    '''
    empirical covariance and inverse_covariance should be dicts
    K is num clusters
    T is num samples
    '''
    mod_lle = 0
    threshold = 2e-5
    clusterParams = {}
    for cluster, clusterInverse in inverse_covariances.items():
        mod_lle += np.log(np.linalg.det(clusterInverse)) - np.trace(np.dot(empirical_covariances[cluster], clusterInverse))
        clusterParams[cluster] = np.sum(np.abs(clusterInverse) > threshold)
    curr_val = -1
    non_zero_params = 0
    for val in clustered_points:
        if val != curr_val:
            non_zero_params += clusterParams[val]
            curr_val = val
    return non_zero_params * np.log(T) - 2*mod_lle



def solve(window_size=10, number_of_clusters=5, lambda_parameter=11e-2,
    beta=400, maxIters=1000, threshold=2e-5, write_out_file=False,
    input_data=None, prefix_string="", compute_BIC=False,
    logging_level=logging.INFO, num_processes=1):
    '''
    Main method for TICC solver.
    Parameters:
        - window_size: size of the sliding window
        - number_of_clusters: number of clusters
        - lambda_parameter: sparsity parameter
        - beta: temporal consistency parameter
        - maxIters: number of iterations
        - threshold: convergence threshold
        - write_out_file: (bool) if true, prefix_string is output file dir
        - prefix_string: output directory if necessary
        - input_file: location of the data file
    '''
    converged=False
    logging.basicConfig(level=logging_level)
    assert maxIters > 0 # must have at least one iteration
    num_blocks = window_size + 1
    num_stacked = window_size
    switch_penalty = beta # smoothness penalty
    lam_sparse = lambda_parameter # sparsity parameter
    num_clusters = number_of_clusters # Number of clusters

    cluster_reassignment = 20 # number of points to reassign to a 0 cluster
    logging.info("lam_sparse: %s, switch_penalty: %s, num_cluster: %s, num_stacked: %s" % (lam_sparse, switch_penalty, num_clusters, num_stacked))

    ######### Get Data into proper format
    Data = input_data
    # Data = np.loadtxt(input_file, delimiter= ",") 
    (m,n) = Data.shape # m: num of observations, n: size of observation vector
    logging.debug("completed getting the data")

    cluster_reassignment = min(cluster_reassignment, m/float(num_clusters))

    ############
    ##The basic folder to be created
    ###-------INITIALIZATION----------
    # Train test split
    training_indices = getTrainTestSplit(m, num_blocks, num_stacked) #indices of the training samples
    num_train_points = len(training_indices)
    num_test_points = m - num_train_points
    ##Stack the training data
    complete_D_train = np.zeros([num_train_points, num_stacked*n])
    for i in range(num_train_points):
        for k in range(num_stacked):
            if i+k < num_train_points:
                idx_k = training_indices[i+k]
                complete_D_train[i][k*n:(k+1)*n] =  Data[idx_k][0:n]
    # Initialization
    gmm = mixture.GaussianMixture(n_components=num_clusters, covariance_type="full")
    gmm.fit(complete_D_train)
    clustered_points = gmm.predict(complete_D_train) 

    train_cluster_inverse = {}
    log_det_values = {} # log dets of the thetas
    computed_covariance = {} 
    cluster_mean_info = {}
    cluster_mean_stacked_info = {}
    old_clustered_points = None # points from last iteration

    empirical_covariances = {}

    pool = None
    if num_processes > 1:
        pool = Pool(processes=num_processes)


    # PERFORM TRAINING ITERATIONS
    for iters in range(maxIters):
        logging.info("\n\n\nITERATION ### %s" % iters)
        
        ##Get the train and test points
        train_clusters = collections.defaultdict(list) # {cluster: [point indices]}
        for point, cluster in enumerate(clustered_points):
            train_clusters[cluster].append(point)

        len_train_clusters = {k: len(train_clusters[k]) for k in range(num_clusters)}

        # train_clusters holds the indices in complete_D_train 
        # for each of the clusters
        optRes = [None for i in range(num_clusters)] # actual results if only one process
        for cluster in range(num_clusters):
            cluster_length = len_train_clusters[cluster]
            if cluster_length != 0:
                size_blocks = n
                indices = train_clusters[cluster]
                D_train = np.zeros([cluster_length,num_stacked*n])
                for i in range(cluster_length):
                    point = indices[i]
                    D_train[i,:] = complete_D_train[point,:]
                
                cluster_mean_info[num_clusters,cluster] = np.mean(D_train, axis = 0)[(num_stacked-1)*n:num_stacked*n].reshape([1,n])
                cluster_mean_stacked_info[num_clusters,cluster] = np.mean(D_train,axis=0)
                ##Fit a model - OPTIMIZATION    
                probSize = num_stacked * size_blocks
                lamb = np.zeros((probSize,probSize)) + lam_sparse
                S = np.cov(np.transpose(D_train) )
                empirical_covariances[cluster] = S

                rho = 1
                solver = ADMMSolver(lamb, num_stacked, size_blocks, 1, S)
                # apply to process pool
                if pool is not None:
                    optRes[cluster] = pool.apply_async(solver, (1000, 1e-6, 1e-6, False,))
                else:
                    optRes[cluster] = solver(1000, 1e-6, 1e-6, False)

        for cluster in range(num_clusters):
            if optRes[cluster] is None:
                continue
            val = optRes[cluster]
            if pool is not None:
                val = optRes[cluster].get() # val is actually a future
            logging.debug("OPTIMIZATION for Cluster %s DONE!!!" % cluster)
            #THIS IS THE SOLUTION
            S_est = upperToFull(val, 0)
            X2 = S_est
            u, _ = np.linalg.eig(S_est)
            cov_out = np.linalg.inv(X2)

            # Store the log-det, covariance, inverse-covariance, cluster means, stacked means
            log_det_values[num_clusters, cluster] = np.log(np.linalg.det(cov_out))
            computed_covariance[num_clusters,cluster] = cov_out
            train_cluster_inverse[cluster] = X2

        for cluster in range(num_clusters):
            logging.debug("length of cluster %s ----> %s" % (cluster, len_train_clusters[cluster]))

        # update old computed covariance
        old_computed_covariance = computed_covariance
        logging.debug("update the old covariance")

        inv_cov_dict = {} # cluster to inv_cov
        log_det_dict = {} # cluster to log_det
        for cluster in range(num_clusters):
            cov_matrix = computed_covariance[num_clusters,cluster][0:(num_blocks-1)*n,0:(num_blocks-1)*n]
            inv_cov_matrix = np.linalg.inv(cov_matrix)
            log_det_cov = np.log(np.linalg.det(cov_matrix))# log(det(sigma2|1))
            inv_cov_dict[cluster] = inv_cov_matrix
            log_det_dict[cluster] = log_det_cov

        # -----------------------SMOOTHENING
        # For each point compute the LLE 
        logging.debug("begin the smoothening algorithm")

        LLE_all_points_clusters = np.zeros([len(clustered_points),num_clusters])
        for point in range(len(clustered_points)):
            if point + num_stacked-1 < complete_D_train.shape[0]:
                for cluster in range(num_clusters):
                    cluster_mean = cluster_mean_info[num_clusters,cluster] 
                    cluster_mean_stacked = cluster_mean_stacked_info[num_clusters,cluster] 
                    x = complete_D_train[point,:] - cluster_mean_stacked[0:(num_blocks-1)*n]
                    inv_cov_matrix = inv_cov_dict[cluster]
                    log_det_cov = log_det_dict[cluster]
                    lle = np.dot(   x.reshape([1,(num_blocks-1)*n]), np.dot(inv_cov_matrix,x.reshape([n*(num_blocks-1),1]))  ) + log_det_cov
                    LLE_all_points_clusters[point,cluster] = lle
        
        ##Update cluster points - using NEW smoothening
        clustered_points = updateClusters(LLE_all_points_clusters,switch_penalty = switch_penalty)

        if iters != 0:
            cluster_norms = [(np.linalg.norm(old_computed_covariance[num_clusters,i]), i) for i in range(num_clusters)]
            norms_sorted = sorted(cluster_norms,reverse = True)
            # clusters that are not 0 as sorted by norm
            valid_clusters = [cp[1] for cp in norms_sorted if len_train_clusters[cp[1]] != 0]

            # Add a point to the empty clusters 
            # assuming more non empty clusters than empty ones
            counter = 0
            for cluster in range(num_clusters):
                if len_train_clusters[cluster] == 0:
                    cluster_selected = valid_clusters[counter] # a cluster that is not len 0
                    counter = (counter+1) % len(valid_clusters)
                    start_point = np.random.choice(train_clusters[cluster_selected]) # random point number from that cluster
                    for i in range(0, cluster_reassignment):
                        # put cluster_reassignment points from point_num in this cluster
                        point_to_move = start_point + i
                        if point_to_move >= len(clustered_points):
                            break
                        clustered_points[point_to_move] = cluster
                        computed_covariance[num_clusters,cluster] = old_computed_covariance[num_clusters,cluster_selected]
                        cluster_mean_stacked_info[num_clusters,cluster] = complete_D_train[point_to_move,:]
                        cluster_mean_info[num_clusters,cluster] = complete_D_train[point_to_move,:][(num_stacked-1)*n:num_stacked*n]
        

        for cluster in range(num_clusters):
            logging.debug("length of cluseter %s ----> %s" % (cluster, sum([x== cluster for x in clustered_points]) ))

        if np.array_equal(old_clustered_points,clustered_points):
            logging.info("\n\n\n\nCONVERGED!!! BREAKING EARLY!!!")
            converged=True
            break
        old_clustered_points = clustered_points
        # end of training

    if pool is not None:
        pool.close()
        pool.join()

    #########################################################
    ##DONE WITH EVERYTHING 
    if compute_BIC:
        bic = computeBIC(num_clusters, m, clustered_points,train_cluster_inverse, empirical_covariances)
        return (clustered_points, train_cluster_inverse, bic, converged)
    return (clustered_points, train_cluster_inverse)

#######################################################################################################################################################################



