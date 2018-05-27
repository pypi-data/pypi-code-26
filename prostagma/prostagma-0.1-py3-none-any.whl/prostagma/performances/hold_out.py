from sklearn.utils import shuffle

from prostagma.performances.performance import Performance

class HoldOut(Performance):
	def __init__(self, val_samples=100):
		super(HoldOut, self).__init__()
		self.val_samples = val_samples
		"""
			@args
				val_samples : int -> number of samples
					used to validate the training.
		"""

	def fit(X_train, y_train, model, parameters=None):
		"""
			The method computes a simple hold out validation
			on the training data, returning the results 
			obtained.

			@args
				X_train : numpy array -> features
				y_train ; numpy array -> labels
				model : method to create the Keras model
				parameters : dictionary of parameters based on 
					the defined model
			@return
				metric : float -> score obtained on the
					validation set
		"""
		
		print("Validating the Model... ")
		X_train, y_train = shuffle(X_train, y_train)
		val_x = X_train[0:self.val_samples] 
		val_y = y_train[0:self.val_samples]
		train_x = X_train[self.val_samples:]
		train_y = y_train[self.val_samples:]
			network = model(parameters)
			network.fit(
				x=train_x, 
				y=train_y, 
				epochs=self.epochs, 
				batch_size=self.batch_size,
				verbose=0
				)
			_ , metric = network.evaluate(x=val_x, y=val_y, verbose=0)
		return metric
		