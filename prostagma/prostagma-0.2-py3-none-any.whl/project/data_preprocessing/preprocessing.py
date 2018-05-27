from tensorflow.python.keras.utils import to_categorical

class Preprocessor(object):
	"""docstring for Preprocessor"""
	def __init__(self, train_samples, 
			test_samples, val_samples):
		super(Preprocessor, self).__init__()
		self.train_samples = train_samples
		self.test_samples = test_samples
		self.val_samples = val_samples

	def fit_transform(self, X, y):

		# Reshape Fetaures
		X = X.reshape(70000, 28, 28, 1)

		# Rescale Fetaures
		X = self.rescale_features(X)

		# Labels to Categorical
		y = to_categorical(y, 10)

		# Train, test, validation split
		X_train, y_train, X_test, y_test, X_val, y_val \
			= self.train_test_validation_split(X, y)

		return X_train, y_train, X_test, y_test, X_val, y_val

	def rescale_features(self, X):
		X = X.astype("float32")
		X /= 255
		return X

	def train_test_validation_split(self, features, labels):
		
		X_test = features[0:self.test_samples]
		y_test = labels[0:self.test_samples]

		X_val = features[self.test_samples:self.test_samples + self.val_samples]
		y_val = labels[self.test_samples:self.test_samples + self.val_samples]

		X_train = features[self.test_samples + self.val_samples: \
			self.test_samples + self.val_samples + self.train_samples]
		y_train = labels[self.test_samples + self.val_samples: \
			self.test_samples + self.val_samples + self.train_samples]
		
		return X_train, y_train, X_test, y_test, X_val, y_val

		