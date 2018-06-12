import numpy as np


def ndcg(r):
    """
    input:
        - r (list): relevance scores in rank order
    """
    # actual dcg
    adcg = dcg(r)
    # find ideal dcg
    # sort the list
    ir = sorted(r, reverse=True)
    idcg = dcg(ir)
    ndcg = adcg/idcg
    return ndcg

def dcg(r, n=None, exp=True):
    """
    input:
        - r (array): array of relevance scores in rank order
        - n (integer): DCG@n
        - exp (boolean): use exponential formula
    """
    r = np.array(r)
    if n:
        r = r[:n]
    # exponential formula?
    if exp:
        gain = 2**r +1
    else:
        gain = r
    # sum the relevance scores, logarithmically discounted by rank
    discount = np.log2(np.arange(len(r))+2)
    return np.sum(gain / discount)


def precision(r, n=None):
    """
    input:
        - r (array): array of boolean relevance scores in rank order
        - n (integer): precision@n
    """
    if not all(i in [0,1] for i in r) or not all(isinstance(i,bool) for i in a):
        raise TypeError('Wrong types, array should be boolean')
    r = np.array(r)
    if n:
        r = r[:n]
    return np.sum(r)

def average_precision(r, n=None):
    """
    input:
        - r (array): array of boolean relevance scores in rank order
        - n (integer): precision@n
    """
    if not all(i in [0,1] for i in r) or not all(isinstance(i,bool) for i in r):
        raise TypeError('Wrong types, array should be boolean')
    r = np.array(r)
    if n:
        r = r[:n]
    correct = 0
    score = 0
    for idx, i in enumerate(r):
        if i:
            correct += 1
            print(i, correct, idx+1)
            score += correct/(idx+1)
    return score/correct



if __name__=='__main__':
    r = [1.0, 1.2, 0.8, 0.4, 0.9]
    #print(dcg(r))
    #print(ndcg(r))
    print(average_precision([True, False, False, True]))
