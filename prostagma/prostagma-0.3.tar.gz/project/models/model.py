from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Dropout, Conv2D, Activation, MaxPooling2D, Flatten
from tensorflow.python.keras.optimizers import Adam
from tensorflow.python.keras.callbacks import ModelCheckpoint, TensorBoard

class Model(object):
    def __init__(self, log_dir=None, model_path=None):
        super(Model, self).__init__()
        """
			self.accuracy represents how good is a certain model. 
			When trained/tested the variable is updated based
			on the validation metric.
        """
        self.log_dir = log_dir
        self.model_path = model_path
        self.model = self.build_model()
        self.checkpointers = self.build_checkpointers()

    def build_model(self, parameters=None):        
        
        # Get parameters
        try:
            dropout = parameters["dropout"]
            learning_rate = parameters["learning_rate"]
        except:
            dropout = 0.1
            learning_rate = 0.001

        # Define Model architecture
        model = Sequential()
        model.add(Conv2D(32, (3, 3), padding="SAME", input_shape=(28, 28, 1)))
        model.add(Activation("relu"))
        model.add(Conv2D(32, (3, 3)))
        model.add(Activation("relu"))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(dropout))

        model.add(Conv2D(64, (3, 3), padding="SAME"))
        model.add(Activation("relu"))
        model.add(Conv2D(64, (3, 3)))
        model.add(Activation("relu"))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(dropout))

        model.add(Flatten())
        model.add(Dense(512))
        model.add(Activation("relu"))
        model.add(Dropout(dropout))
        model.add(Dense(10))
        model.add(Activation("softmax"))

        # Compile the model
        model.compile(
            optimizer=Adam(learning_rate),
            loss="categorical_crossentropy", 
            metrics=["accuracy"])

        return model

    def build_checkpointers(self):
        checkpointers = []
        if self.model_path is not None:
            checkpointer = ModelCheckpoint(filepath=self.model_path + '.h5', 
                monitor='val_loss', verbose=1, save_best_only=True, period=10)
            checkpointers.append(checkpointer)
        
        if self.log_dir is not None:
            tensorboard = TensorBoard(log_dir=self.log_dir, histogram_freq=0, 
                batch_size=32, write_graph=True, write_grads=False, write_images=False)
            checkpointers.append(tensorboard)

        return checkpointers

    def fit(self, X_train, y_train, epochs, batch_size, X_val=None, y_val=None):
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            validation_data=(X_val, y_val),
            batch_size=batch_size,
            verbose=1,
            callbacks=self.checkpointers)

        return history

    def evaluate(self, X_test, y_test):
        loss, metric = self.model.evaluate(X_test, y_test, verbose=0)
        return loss, metric

    def predict(self, X):
        y_pred = self.model.predict(X)
        return y_pred

    def restore_weights(self):
        try:
            self.model.load_weights(self.model_path + ".h5")
            print("Loaded model from disk")
        except OSError:
            pass
        return

    def run_model(self, X_train, y_train, X_test, y_test, 
        X_val, y_val, train, test):
        
        # Train the model
        if train == True:
            history = self.fit(X_train, y_train, X_val, y_val)
        
        # Test the model
        if test == True:
            score = self.evaluate(X_test, y_test)
            print("SCORE: ", score)


        return
		