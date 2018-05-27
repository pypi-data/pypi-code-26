import numpy as np

from keras.datasets import mnist

class Loader(object):
	"""docstring for Loader"""
	def __init__(self, number_of_samples):
		super(Loader, self).__init__()
		self.number_of_samples = number_of_samples

	def load_data(self):
		(X_train, y_train), (X_val, y_val) = mnist.load_data()
		X = np.concatenate((X_train, X_val), axis=0)
		y = np.concatenate((y_train, y_val), axis=0)
		return X, y
		