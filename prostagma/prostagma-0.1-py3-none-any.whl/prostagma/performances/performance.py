

class Performance(object):
	"""docstring for Perfomance"""
	def __init__(self, epochs, batch_size):
		super(Performance, self).__init__()
		self.epochs = epochs
		self.batch_size = batch_size

	def fit(self, X_train, y_train, model, parameters=None):
		raise NotImplementedError
		