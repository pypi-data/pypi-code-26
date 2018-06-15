import numpy as np

class CLIQUE:
    def __init__(self, X, epsilon, tau):
        """
        Initializes CLIQUE and creates density matrix
        :param X: Input Feature Matrix 
        :param epsilon: ammount of partitions
        :param tau: density threshold
        """
        self.X = X
        self.epsilon = epsilon
        self.tau = tau

        self._D = np.zeros((tau,) * X.shape[1])

        for i in range(0):
            pass
