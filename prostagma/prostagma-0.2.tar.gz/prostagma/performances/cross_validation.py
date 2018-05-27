import numpy as np

from prostagma.performances.performance import Performance

class CrossValidation(Performance):
	def __init__(self, epochs=500, batch_size=32, k_fold=5):
		super(CrossValidation, self).__init__(
			epochs=epochs, batch_size=batch_size)
		"""
			@args: 
				k_fold -> int : number of fold to used.
		"""
		self.k_fold = k_fold

	def fit(self, X_train, y_train, model, parameters=None):
		"""
			The method computes k-fold cross validation
			on the training data, returning the results 
			obtained for each partition.

			@args
				X_train : numpy array -> features
				y_train ; numpy array -> labels
				model : method to create the Keras model
				parameters : dictionary of parameters based on 
					the defined model
			@return
				scores : numpy array -> all the results from 
					different partitions.
		"""

		scores = []
		val_samples = int(len(X_train) / self.k_fold)
		for fold in range(0, self.k_fold):
			print("Processing Fold: ", fold)
			val_x = X_train[fold * val_samples: (fold + 1) * val_samples] 
			val_y = y_train[fold * val_samples: (fold + 1) * val_samples]
			train_x = np.concatenate([X_train[:fold * val_samples], X_train[(fold + 1) * val_samples:]], axis=0)
			train_y = np.concatenate([y_train[:fold * val_samples], y_train[(fold + 1) * val_samples:]], axis=0)
			network = model(parameters)
			network.fit(
				x=train_x, 
				y=train_y, 
				epochs=self.epochs, 
				batch_size=self.batch_size,
				verbose=0
				)
			_ , metric = network.evaluate(x=val_x, y=val_y, verbose=0)
			scores.append(metric)
		scores = np.asarray(scores)
		return scores

