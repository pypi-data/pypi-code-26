import numpy as np

from itertools import product

from prostagma.techniques.technique import SearchTechnique
from prostagma.performances.cross_validation import CrossValidation
from sklearn.grid_search import ParameterGrid

class GridSearch(SearchTechnique):
	"""
		The class implement the simple Grid Search 
		algorithm to find the best parameters using 
		Cross Validation. 
	"""
	def __init__(self, parameters, model, 
			performance_validator=CrossValidation()):
		super(GridSearch, self).__init__(parameters=parameters, 
			model=model, performance_validator=performance_validator)

	def fit(self, X_train, y_train):
		"""
			The method computes a score for each combination of 
			hyperparameters using the performance validator

			@args
				X_train : numpy array -> features
				y_train : numpy array -> labels

			@return
				all_scores : numpy array -> all the mean scores
					obtained using the performance validator	
		"""
		all_scores = []
		grid = ParameterGrid(self.parameters)
		for params in grid:
			print("Validating the model with: ", params)
			scores = self.performance_validator.fit(X_train, y_train, self.model, params)
			all_scores.append((scores.mean(), scores.std()))

			if scores.mean() > self.best_score[0]:
				self.best_score = (scores.mean(), scores.std())
				self.best_param = params
		all_scores = np.asarray(scores)
		return all_scores



		