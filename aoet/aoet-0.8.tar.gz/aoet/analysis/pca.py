import numpy as np

def pca_projection(X, k=2):
    Xn, mu, sigma = normalize_features(X)
    U, S, V = pca(Xn)
    return project_data(X, U, k)


def project_data(X, U, K):
    Z = np.zeros((X.shape[0], K))
    for i in range(0, X.shape[0]):
        for k in range(0, K):
            x = X[i, :]
            Z[i, k] = x.dot(U[:, k])
    return Z


def pca(X):
    m = X.shape[0]
    the_sigma = X.transpose().dot(X) / m
    return np.linalg.svd(the_sigma)


def normalize_features(X):
    mu = np.mean(X, 0)
    Xn = X - mu
    sigma = np.std(Xn, 0)
    for i in range(sigma.shape[0]):
        if sigma[i] == 0:
            sigma[i] = 1
    Xn = Xn / sigma
    return Xn, mu, sigma